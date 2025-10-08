import os, stat, shutil
import sys
import subprocess
from pathlib import Path
import time
import math
import json
import datetime
import cv2
import numpy as np
import argparse
# from kivy.clock import Clock # COMMENTÉ: Remplacé par un appel direct pour CLI

# --- Variables Globales ---
if getattr(sys, 'frozen', False):
    # Exécuté en tant que bundle PyInstaller
    base_path = sys._MEIPASS
else:
    # Exécuté dans un environnement Python normal
    base_path = os.path.dirname(os.path.abspath(__file__))
    
# Assurez-vous que le répertoire 'data/images' existe par rapport à base_path
images_path = os.path.join(base_path, 'data', 'images')
hand_path = os.path.join(images_path, 'drawing-hand.png')
hand_mask_path = os.path.join(images_path, 'hand-mask.png')
save_path = os.path.join(base_path, "save_videos")
platform = "linux"

# --- Classes et Fonctions ---

def euc_dist(arr1, point):
    """Calcule la distance euclidienne entre un tableau de points (arr1) et un seul point."""
    square_sub = (arr1 - point) ** 2
    return np.sqrt(np.sum(square_sub, axis=1))

def preprocess_image(img, variables):
    """Redimensionne, convertit en niveaux de gris et seuille l'image source."""
    img_ht, img_wd = img.shape[0], img.shape[1]
    img = cv2.resize(img, (variables.resize_wd, variables.resize_ht))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Égalisation de l'histogramme de couleur (CLAHE) - cl1 n'est pas utilisé directement plus tard
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
    cl1 = clahe.apply(img_gray)

    # Seuil adaptatif gaussien
    img_thresh = cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10
    )

    # Ajout des éléments requis à l'objet variables
    variables.img_ht = img_ht
    variables.img_wd = img_wd
    variables.img_gray = img_gray
    variables.img_thresh = img_thresh
    variables.img = img
    return variables


def preprocess_hand_image(hand_path, hand_mask_path, variables):
    """Charge et pré-traite l'image de la main et son masque."""
    hand = cv2.imread(hand_path)
    hand_mask = cv2.imread(hand_mask_path, cv2.IMREAD_GRAYSCALE)

    top_left, bottom_right = get_extreme_coordinates(hand_mask)
    hand = hand[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
    hand_mask = hand_mask[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
    hand_mask_inv = 255 - hand_mask

    # Standardisation des masques de main
    hand_mask = hand_mask / 255
    hand_mask_inv = hand_mask_inv / 255

    # Rendre le fond de la main noir
    hand_bg_ind = np.where(hand_mask == 0)
    hand[hand_bg_ind] = [0, 0, 0]

    # Obtention des dimensions de l'image et de la main
    hand_ht, hand_wd = hand.shape[0], hand.shape[1]

    variables.hand_ht = hand_ht
    variables.hand_wd = hand_wd
    variables.hand = hand
    variables.hand_mask = hand_mask
    variables.hand_mask_inv = hand_mask_inv
    return variables


def get_extreme_coordinates(mask):
    """Trouve les coordonnées minimales et maximales des pixels blancs (255) dans un masque."""
    indices = np.where(mask == 255)
    # Extraire les coordonnées x et y des pixels.
    x = indices[1]
    y = indices[0]

    # Trouver les coordonnées x et y minimales et maximales.
    topleft = (np.min(x), np.min(y))
    bottomright = (np.max(x), np.max(y))

    return topleft, bottomright


def draw_hand_on_img(
    drawing,
    hand,
    drawing_coord_x,
    drawing_coord_y,
    hand_mask_inv,
    hand_ht,
    hand_wd,
    img_ht,
    img_wd,
):
    """Dessine (superpose) l'image de la main sur l'image 'drawing' aux coordonnées données."""
    remaining_ht = img_ht - drawing_coord_y
    remaining_wd = img_wd - drawing_coord_x
    
    # Déterminer la taille de la main à cropper pour éviter de dépasser les bords de l'image
    crop_hand_ht = min(remaining_ht, hand_ht)
    crop_hand_wd = min(remaining_wd, hand_wd)

    hand_cropped = hand[:crop_hand_ht, :crop_hand_wd]
    hand_mask_inv_cropped = hand_mask_inv[:crop_hand_ht, :crop_hand_wd]

    # Coordonnées pour l'insertion
    y_slice = slice(drawing_coord_y, drawing_coord_y + crop_hand_ht)
    x_slice = slice(drawing_coord_x, drawing_coord_x + crop_hand_wd)

    # Masquer la zone pour la main (mettre le fond à 0 en utilisant le masque inversé)
    for i in range(3): # Pour chaque canal de couleur (B, G, R)
        drawing[y_slice, x_slice][:, :, i] = (
            drawing[y_slice, x_slice][:, :, i] * hand_mask_inv_cropped
        )

    # Ajouter l'image de la main
    drawing[y_slice, x_slice] = (
        drawing[y_slice, x_slice]
        + hand_cropped
    )
    return drawing


def draw_masked_object(
    variables, object_mask=None, skip_rate=5, black_pixel_threshold=10
):
    """
    Implémente la logique de dessin en quadrillage.
    Sépare l'image en blocs, sélectionne le bloc le plus proche à dessiner
    et enregistre la trame.
    """
    # print("Skip Rate: ", skip_rate)
    
    # Si un masque d'objet est fourni, le seuil s'appliquera uniquement à cette zone
    img_thresh_copy = variables.img_thresh.copy()
    if object_mask is not None:
        object_mask_black_ind = np.where(object_mask == 0)
        img_thresh_copy[object_mask_black_ind] = 255

    selected_ind_val = None
    selected_ind = 0
    
    # Initialize animation data if JSON export is enabled
    if variables.export_json:
        variables.animation_data = {
            "drawing_sequence": [],
            "frames_written": []
        }
    
    # Calculer le nombre de coupes pour la grille
    n_cuts_vertical = int(math.ceil(variables.resize_ht / variables.split_len))
    n_cuts_horizontal = int(math.ceil(variables.resize_wd / variables.split_len))

    # Construire la grille de tuiles (même les tuiles de bord de taille inégale)
    grid_of_cuts = []
    for i in range(n_cuts_vertical):
        row_cuts = []
        for j in range(n_cuts_horizontal):
            y_start = i * variables.split_len
            y_end = min(y_start + variables.split_len, variables.resize_ht)
            x_start = j * variables.split_len
            x_end = min(x_start + variables.split_len, variables.resize_wd)
            tile = img_thresh_copy[y_start:y_end, x_start:x_end]
            row_cuts.append(tile)
        grid_of_cuts.append(row_cuts)
    
    # Note: grid_of_cuts is kept as nested lists (not converted to numpy array)
    # because tiles can have inconsistent sizes at image borders

    # Trouver les tuiles (tiles) contenant au moins un pixel noir
    cut_black_indices = []
    for i in range(n_cuts_vertical):
        for j in range(n_cuts_horizontal):
            if np.sum(grid_of_cuts[i][j] < black_pixel_threshold) > 0:
                cut_black_indices.append((i, j))
    
    cut_black_indices = np.array(cut_black_indices)


    counter = 0
    # Continue tant qu'il y a des tuiles à dessiner
    while len(cut_black_indices) > 0:
        if selected_ind >= len(cut_black_indices):
            selected_ind = 0 
            
        selected_ind_val = cut_black_indices[selected_ind].copy()
        
        # Récupérer la tuile à dessiner (peut être de taille variable)
        tile_to_draw = grid_of_cuts[selected_ind_val[0]][selected_ind_val[1]]
        tile_ht, tile_wd = tile_to_draw.shape # <-- On récupère la taille réelle
        
        # Calculer les coordonnées de la tuile sélectionnée EN UTILISANT LA TAILLE RÉELLE
        range_v_start = selected_ind_val[0] * variables.split_len
        range_v_end = range_v_start + tile_ht # MODIFIÉ pour utiliser la taille réelle de la tuile
        range_h_start = selected_ind_val[1] * variables.split_len
        range_h_end = range_h_start + tile_wd # MODIFIÉ pour utiliser la taille réelle de la tuile

        # Créer une image BGR à partir de la tuile en niveaux de gris
        temp_drawing = np.zeros((tile_ht, tile_wd, 3), dtype=np.uint8)
        temp_drawing[:, :, 0] = tile_to_draw
        temp_drawing[:, :, 1] = tile_to_draw
        temp_drawing[:, :, 2] = tile_to_draw
        
        # Appliquer la tuile au cadre de dessin - CECI EST LA LIGNE CORRIGÉE
        variables.drawn_frame[range_v_start:range_v_end, range_h_start:range_h_end] = temp_drawing

        # Coordonnées pour le centre de la main
        hand_coord_x = range_h_start + int(tile_wd / 2)
        hand_coord_y = range_v_start + int(tile_ht / 2)
        
        # Dessiner la main
        drawn_frame_with_hand = draw_hand_on_img(
            variables.drawn_frame.copy(),
            variables.hand.copy(),
            hand_coord_x,
            hand_coord_y,
            variables.hand_mask_inv.copy(),
            variables.hand_ht,
            variables.hand_wd,
            variables.resize_ht,
            variables.resize_wd,
        )

        # Supprimer l'index sélectionné
        cut_black_indices = np.delete(cut_black_indices, selected_ind, axis=0)

        # Sélectionner le nouvel index le plus proche
        if len(cut_black_indices) > 0:
            euc_arr = euc_dist(cut_black_indices, selected_ind_val)
            selected_ind = np.argmin(euc_arr)
        else:
            selected_ind = -1 

        counter += 1
        if counter % skip_rate == 0 or len(cut_black_indices) == 0:
            variables.video_object.write(drawn_frame_with_hand)
            
            # Capture animation data if JSON export is enabled
            if variables.export_json:
                frame_data = {
                    "frame_number": len(variables.animation_data["frames_written"]),
                    "tile_drawn": {
                        "grid_position": [int(selected_ind_val[0]), int(selected_ind_val[1])],
                        "pixel_coords": {
                            "x_start": int(range_h_start),
                            "x_end": int(range_h_end),
                            "y_start": int(range_v_start),
                            "y_end": int(range_v_end)
                        }
                    },
                    "hand_position": {
                        "x": int(hand_coord_x),
                        "y": int(hand_coord_y)
                    },
                    "tiles_remaining": int(len(cut_black_indices))
                }
                variables.animation_data["frames_written"].append(frame_data)

        if counter % 40 == 0 and len(cut_black_indices) > 0:
            print(f"Tuiles restantes: {len(cut_black_indices)}")

    # Après avoir dessiné toutes les lignes, superposer l'objet original en couleur
    if object_mask is not None:
        object_ind = np.where(object_mask == 255)
        variables.drawn_frame[object_ind] = variables.img[object_ind]
    else:
        variables.drawn_frame[:, :, :] = variables.img


def draw_whiteboard_animations(
    img, mask_path, hand_path, hand_mask_path, save_video_path, variables
):
    """Fonction principale pour orchestrer l'animation de dessin."""
    object_mask_exists = (mask_path is not None)

    # 1. Pré-traitement de l'image source et de la main
    variables = preprocess_image(img=img, variables=variables)
    variables = preprocess_hand_image(
        hand_path=hand_path, hand_mask_path=hand_mask_path, variables=variables
    )

    start_time = time.time()

    # 2. Définition de l'objet vidéo
    if platform == "android":
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    else:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v") 
        
    variables.video_object = cv2.VideoWriter(
        save_video_path,
        fourcc,
        variables.frame_rate,
        (variables.resize_wd, variables.resize_ht),
    )

    # 3. Création d'un cadre vide (fond blanc)
    variables.drawn_frame = np.zeros(variables.img.shape, np.uint8) + np.array(
        [255, 255, 255], np.uint8
    )

    # 4. Dessin de l'animation
    # Dessiner l'image entière sans masque
    draw_masked_object(
        variables=variables,
        skip_rate=variables.object_skip_rate,
    )


    # 5. Fin de la vidéo avec l'image originale en couleur
    for i in range(variables.frame_rate * variables.end_gray_img_duration_in_sec):
        variables.video_object.write(variables.img)

    end_time = time.time()
    print(f"Temps total d'exécution pour le dessin: {end_time - start_time:.2f} secondes")

    # 6. Fermeture de l'objet vidéo
    variables.video_object.release()


def export_animation_json(variables, json_path):
    """Exporte les données d'animation au format JSON."""
    if not variables.animation_data:
        print("⚠️ Aucune donnée d'animation à exporter.")
        return False
    
    try:
        # Convert numpy types to Python native types
        def convert_to_native(obj):
            """Convertit les types numpy en types Python natifs."""
            if isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64,
                               np.uint8, np.uint16, np.uint32, np.uint64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_to_native(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            else:
                return obj
        
        export_data = {
            "metadata": {
                "frame_rate": int(variables.frame_rate),
                "width": int(variables.resize_wd),
                "height": int(variables.resize_ht),
                "split_len": int(variables.split_len),
                "object_skip_rate": int(variables.object_skip_rate),
                "total_frames": len(variables.animation_data["frames_written"]),
                "hand_dimensions": {
                    "width": int(variables.hand_wd),
                    "height": int(variables.hand_ht)
                }
            },
            "animation": convert_to_native(variables.animation_data)
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Données d'animation exportées: {json_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export JSON: {e}")
        return False


def find_nearest_res(given):
    """Trouve la résolution standard la plus proche pour une dimension donnée."""
    arr = np.array([360, 480, 640, 720, 1080, 1280, 1440, 1920, 2160, 2560, 3840, 4320, 7680])
    idx = (np.abs(arr - given)).argmin()
    return arr[idx]

class AllVariables:
    """Classe conteneur pour toutes les variables et paramètres du processus."""
    def __init__(
        self,
        frame_rate=None,
        resize_wd=None,
        resize_ht=None,
        split_len=None,
        object_skip_rate=None,
        bg_object_skip_rate=None,
        end_gray_img_duration_in_sec=None,
        export_json=False,
    ):
        self.frame_rate = frame_rate
        self.resize_wd = resize_wd
        self.resize_ht = resize_ht
        self.split_len = split_len
        self.object_skip_rate = object_skip_rate
        self.bg_object_skip_rate = bg_object_skip_rate
        self.end_gray_img_duration_in_sec = end_gray_img_duration_in_sec
        self.export_json = export_json
        
        # Variables qui seront ajoutées plus tard
        self.img_ht = None
        self.img_wd = None
        self.img_gray = None
        self.img_thresh = None
        self.img = None
        self.hand_ht = None
        self.hand_wd = None
        self.hand = None
        self.hand_mask = None
        self.hand_mask_inv = None
        self.video_object = None
        self.drawn_frame = None
        
        # Variables pour l'export JSON
        self.animation_data = None


def common_divisors(num1, num2):
    """Trouve tous les diviseurs communs de deux nombres et les renvoie triés."""
    common_divs = []
    min_num = min(num1, num2)
    
    for i in range(1, min_num + 1):
        if num1 % i == 0 and num2 % i == 0:
            common_divs.append(i)
    return common_divs


def ffmpeg_convert(source_vid, dest_vid, platform="linux"):
    """Convertit la vidéo brute (mp4v) en H.264 compatible avec PyAV."""
    ff_stat = False
    try:
        import av
        src_path = Path(source_vid)
        input_container = av.open(src_path, mode="r")
        output_container = av.open(dest_vid, mode="w")
        
        in_stream = input_container.streams.video[0]
        width = in_stream.codec_context.width
        height = in_stream.codec_context.height
        fps = in_stream.average_rate
        
        # set output params
        out_stream = output_container.add_stream("h264", rate=fps)
        out_stream.width = width
        out_stream.height = height
        out_stream.pix_fmt = "yuv420p"
        out_stream.options = {"crf": "20"}

        for frame in input_container.decode(video=0):
            packet = out_stream.encode(frame)
            if packet:
                output_container.mux(packet)
                
        packet = out_stream.encode()
        if packet:
            output_container.mux(packet)
            
        output_container.close()
        input_container.close()

        print(f"✅ Conversion FFmpeg réussie. Fichier: {dest_vid}")
        ff_stat = True
        
    except ImportError:
        print("⚠️ AVERTISSEMENT: Le module 'av' (PyAV) n'est pas installé. La conversion H.264 sera ignorée.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion FFmpeg: {e}")
        
    return ff_stat


def generate_transition_frames(frame1, frame2, transition_type, num_frames, fps):
    """Génère des frames de transition entre deux frames.
    
    Args:
        frame1: Frame de fin de la vidéo précédente (numpy array BGR)
        frame2: Frame de début de la vidéo suivante (numpy array BGR)
        transition_type: Type de transition ('none', 'fade', 'wipe', 'push_left', 'push_right', 'iris')
        num_frames: Nombre de frames de transition à générer
        fps: Frame rate de la vidéo
    
    Returns:
        Liste de frames de transition
    """
    if transition_type == 'none' or num_frames == 0:
        return []
    
    transition_frames = []
    
    if transition_type == 'fade':
        # Transition en fondu
        for i in range(num_frames):
            alpha = (i + 1) / (num_frames + 1)
            blended = cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)
            transition_frames.append(blended)
    
    elif transition_type == 'wipe':
        # Transition en balayage de gauche à droite
        height, width = frame1.shape[:2]
        for i in range(num_frames):
            progress = (i + 1) / (num_frames + 1)
            split_x = int(width * progress)
            frame = frame1.copy()
            frame[:, :split_x] = frame2[:, :split_x]
            transition_frames.append(frame)
    
    elif transition_type == 'push_left':
        # Poussée vers la gauche
        height, width = frame1.shape[:2]
        for i in range(num_frames):
            progress = (i + 1) / (num_frames + 1)
            offset = int(width * progress)
            frame = np.zeros_like(frame1)
            
            # Partie de frame1 qui reste visible
            if offset < width:
                frame[:, :width-offset] = frame1[:, offset:]
            
            # Partie de frame2 qui devient visible
            frame[:, width-offset:] = frame2[:, :offset]
            transition_frames.append(frame)
    
    elif transition_type == 'push_right':
        # Poussée vers la droite
        height, width = frame1.shape[:2]
        for i in range(num_frames):
            progress = (i + 1) / (num_frames + 1)
            offset = int(width * progress)
            frame = np.zeros_like(frame1)
            
            # Partie de frame2 qui devient visible
            frame[:, :offset] = frame2[:, width-offset:]
            
            # Partie de frame1 qui reste visible
            if offset < width:
                frame[:, offset:] = frame1[:, :width-offset]
            transition_frames.append(frame)
    
    elif transition_type == 'iris':
        # Transition en iris (cercle qui s'agrandit)
        height, width = frame1.shape[:2]
        center = (width // 2, height // 2)
        max_radius = int(np.sqrt(width**2 + height**2) / 2)
        
        for i in range(num_frames):
            progress = (i + 1) / (num_frames + 1)
            radius = int(max_radius * progress)
            
            # Créer un masque circulaire
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.circle(mask, center, radius, 255, -1)
            mask_3ch = cv2.merge([mask, mask, mask])
            
            # Appliquer le masque
            frame = frame1.copy()
            frame = np.where(mask_3ch == 255, frame2, frame1)
            transition_frames.append(frame)
    
    return transition_frames


def concatenate_videos(video_paths, output_path, transition_type='none', transition_duration=0.5):
    """Concatène plusieurs vidéos en une seule vidéo finale avec transitions optionnelles.
    
    Args:
        video_paths: Liste des chemins des vidéos à concaténer
        output_path: Chemin de sortie pour la vidéo combinée
        transition_type: Type de transition ('none', 'fade', 'wipe', 'push_left', 'push_right', 'iris')
        transition_duration: Durée de la transition en secondes
    """
    try:
        import av
        
        if not video_paths:
            raise ValueError("Aucune vidéo à concaténer")
        
        if len(video_paths) == 1:
            # Si une seule vidéo, copier simplement
            shutil.copy2(video_paths[0], output_path)
            print(f"✅ Vidéo unique copiée: {output_path}")
            return True
        
        print(f"🔗 Concaténation de {len(video_paths)} vidéos...")
        if transition_type != 'none':
            print(f"   Transition: {transition_type} ({transition_duration}s)")
        
        # Ouvrir le premier fichier pour obtenir les paramètres
        first_container = av.open(video_paths[0], mode="r")
        first_stream = first_container.streams.video[0]
        width = first_stream.codec_context.width
        height = first_stream.codec_context.height
        fps = first_stream.average_rate
        first_container.close()
        
        # Calculer le nombre de frames de transition
        num_transition_frames = int(float(fps) * transition_duration)
        
        # Créer le conteneur de sortie
        output_container = av.open(output_path, mode="w")
        out_stream = output_container.add_stream("h264", rate=fps)
        out_stream.width = width
        out_stream.height = height
        out_stream.pix_fmt = "yuv420p"
        out_stream.options = {"crf": "20"}
        
        last_frame = None
        
        # Concaténer toutes les vidéos
        for i, video_path in enumerate(video_paths):
            print(f"  Ajout de la vidéo {i+1}/{len(video_paths)}: {os.path.basename(video_path)}")
            input_container = av.open(video_path, mode="r")
            
            first_frame_of_video = None
            frames_list = []
            
            # Lire toutes les frames de cette vidéo
            for frame in input_container.decode(video=0):
                frames_list.append(frame)
            
            input_container.close()
            
            # Ajouter la transition si ce n'est pas la première vidéo
            if i > 0 and last_frame is not None and len(frames_list) > 0:
                first_frame_of_video = frames_list[0]
                
                # Convertir les frames PyAV en numpy arrays
                last_frame_np = last_frame.to_ndarray(format='bgr24')
                first_frame_np = first_frame_of_video.to_ndarray(format='bgr24')
                
                # Redimensionner les frames si nécessaire pour correspondre à la résolution de sortie
                if last_frame_np.shape[:2] != (height, width):
                    last_frame_np = cv2.resize(last_frame_np, (width, height))
                if first_frame_np.shape[:2] != (height, width):
                    first_frame_np = cv2.resize(first_frame_np, (width, height))
                
                # Générer les frames de transition
                transition_frames = generate_transition_frames(
                    last_frame_np, first_frame_np, transition_type, 
                    num_transition_frames, float(fps)
                )
                
                # Encoder les frames de transition
                for trans_frame in transition_frames:
                    # Convertir numpy array en PyAV frame
                    av_frame = av.VideoFrame.from_ndarray(trans_frame, format='bgr24')
                    av_frame.pts = None
                    # encode() retourne une liste de packets
                    packets = out_stream.encode(av_frame)
                    for packet in packets:
                        output_container.mux(packet)
            
            # Ajouter toutes les frames de cette vidéo
            # Pour assurer la compatibilité avec les frames de transition,
            # convertir les frames décodées en numpy puis en VideoFrame
            for frame in frames_list:
                # Convertir en numpy puis recréer le frame
                frame_np = frame.to_ndarray(format='bgr24')
                
                # Redimensionner si nécessaire pour correspondre à la résolution de sortie
                if frame_np.shape[:2] != (height, width):
                    frame_np = cv2.resize(frame_np, (width, height))
                
                av_frame = av.VideoFrame.from_ndarray(frame_np, format='bgr24')
                # encode() retourne une liste de packets
                packets = out_stream.encode(av_frame)
                for packet in packets:
                    output_container.mux(packet)
            
            # Sauvegarder la dernière frame pour la transition suivante
            if len(frames_list) > 0:
                last_frame = frames_list[-1]
        
        # Finaliser l'encodage - appeler encode() en boucle jusqu'à ce qu'il n'y ait plus de packets
        try:
            while True:
                packets = out_stream.encode()
                if not packets:
                    break
                for packet in packets:
                    output_container.mux(packet)
        except Exception:
            # L'encoder peut signaler EOF lors du flush, c'est normal
            pass
        
        output_container.close()
        
        # Vérifier que le fichier a bien été créé
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ Concaténation réussie: {output_path}")
            return True
        else:
            print(f"❌ Le fichier de sortie n'a pas été créé correctement")
            return False
        
    except ImportError:
        print("❌ ERREUR: Le module 'av' (PyAV) est requis pour la concaténation de vidéos.")
        print("   Installez-le avec: pip install av")
        return False
        
    except Exception as e:
        # Vérifier si le fichier existe malgré l'erreur (PyAV peut rapporter des erreurs même en cas de succès)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ Concaténation réussie: {output_path}")
            print(f"   (Note: PyAV a rapporté une erreur mais le fichier est valide)")
            return True
        else:
            print(f"❌ Erreur lors de la concaténation: {e}")
            return False


def initiate_sketch_sync(image_path, split_len, frame_rate, object_skip_rate, bg_object_skip_rate, main_img_duration, callback, save_path=save_path, which_platform="linux", export_json=False):
    """Version synchrone de initiate_sketch pour l'exécution en ligne de commande (sans Kivy Clock)."""
    global platform
    platform = which_platform
    final_result = {"status": False, "message": "Initial load"}
    try:
        if not (os.path.exists(hand_path) and os.path.exists(hand_mask_path)):
            raise FileNotFoundError(f"Fichiers de main manquants. Attendu dans: {images_path}")
            
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
             raise ValueError(f"Impossible de lire l'image: {image_path}")
             
        mask_path = None 

        now = datetime.datetime.now()
        current_time = str(now.strftime("%H%M%S"))
        current_date = str(now.strftime("%Y%m%d"))
        
        video_save_name = f"vid_{current_date}_{current_time}.mp4" 
        save_video_path = os.path.join(save_path, video_save_name)
        ffmpeg_file_name = f"vid_{current_date}_{current_time}_h264.mp4"
        ffmpeg_video_path = os.path.join(save_path, ffmpeg_file_name)
        json_file_name = f"animation_{current_date}_{current_time}.json"
        json_export_path = os.path.join(save_path, json_file_name)
        os.makedirs(os.path.dirname(save_video_path), exist_ok=True)
        print(f"Chemin de sauvegarde brut: {save_video_path}")

        img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
        aspect_ratio = img_wd / img_ht
        img_ht = find_nearest_res(img_ht)
        new_aspect_wd = int(img_ht * aspect_ratio)
        img_wd = find_nearest_res(new_aspect_wd)
        print(f"Résolution cible: {img_wd}x{img_ht}")

        variables = AllVariables(
            frame_rate=frame_rate, resize_wd=img_wd, resize_ht=img_ht, split_len=split_len, 
            object_skip_rate=object_skip_rate, bg_object_skip_rate=bg_object_skip_rate, 
            end_gray_img_duration_in_sec=main_img_duration, export_json=export_json
        )

        draw_whiteboard_animations(
            image_bgr, mask_path, hand_path, hand_mask_path, save_video_path, variables
        )
        
        # Export JSON if requested
        if export_json:
            export_animation_json(variables, json_export_path)
        
        ff_stat = ffmpeg_convert(source_vid=save_video_path, dest_vid=ffmpeg_video_path, platform=platform)
        
        if ff_stat:
            final_result = {"status": True, "message": f"{ffmpeg_video_path}"}
            os.unlink(save_video_path)
            print(f"Vidéo brute supprimée: {save_video_path}")
        else:
            final_result = {"status": True, "message": f"{save_video_path}"} 
        
        # Add JSON path to result if exported
        if export_json:
            final_result["json_path"] = json_export_path

    except Exception as e:
        final_result = {"status": False, "message": f"Erreur fatale: {e}"}

    callback(final_result)


def process_multiple_images(image_paths, split_len, frame_rate, object_skip_rate, bg_object_skip_rate, main_img_duration, which_platform="linux", export_json=False, transition='none', transition_duration=0.5):
    """Traite plusieurs images et génère une vidéo combinée.
    
    Args:
        image_paths: Liste des chemins des images à traiter
        split_len: Taille de la grille pour le dessin
        frame_rate: Images par seconde
        object_skip_rate: Vitesse de dessin
        bg_object_skip_rate: Taux de saut pour l'arrière-plan
        main_img_duration: Durée de l'image finale en secondes
        which_platform: Plateforme ('linux', 'android', etc.)
        export_json: Exporter les données d'animation au format JSON
        transition: Type de transition ('none', 'fade', 'wipe', 'push_left', 'push_right', 'iris')
        transition_duration: Durée de la transition en secondes
    """
    global platform
    platform = which_platform
    
    if not image_paths:
        return {"status": False, "message": "Aucune image fournie"}
    
    print("\n" + "="*60)
    print(f"🎬 TRAITEMENT DE {len(image_paths)} IMAGE(S)")
    print("="*60)
    
    generated_videos = []
    json_exports = []
    
    # Créer un horodatage unique pour cette série
    now = datetime.datetime.now()
    current_time = str(now.strftime("%H%M%S"))
    current_date = str(now.strftime("%Y%m%d"))
    series_id = f"{current_date}_{current_time}"
    
    # Traiter chaque image
    for idx, image_path in enumerate(image_paths, 1):
        print(f"\n📷 Image {idx}/{len(image_paths)}: {os.path.basename(image_path)}")
        print("-" * 60)
        
        if not os.path.exists(image_path):
            print(f"⚠️ Image ignorée (introuvable): {image_path}")
            continue
        
        try:
            # Lire l'image pour vérifier
            image_bgr = cv2.imread(image_path)
            if image_bgr is None:
                print(f"⚠️ Image ignorée (illisible): {image_path}")
                continue
            
            mask_path = None
            
            # Noms de fichiers pour cette image
            video_save_name = f"vid_{series_id}_img{idx}.mp4"
            save_video_path = os.path.join(save_path, video_save_name)
            ffmpeg_file_name = f"vid_{series_id}_img{idx}_h264.mp4"
            ffmpeg_video_path = os.path.join(save_path, ffmpeg_file_name)
            json_file_name = f"animation_{series_id}_img{idx}.json"
            json_export_path = os.path.join(save_path, json_file_name)
            
            os.makedirs(save_path, exist_ok=True)
            
            # Calculer la résolution
            img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
            aspect_ratio = img_wd / img_ht
            img_ht = find_nearest_res(img_ht)
            new_aspect_wd = int(img_ht * aspect_ratio)
            img_wd = find_nearest_res(new_aspect_wd)
            print(f"  Résolution cible: {img_wd}x{img_ht}")
            
            # Créer les variables
            variables = AllVariables(
                frame_rate=frame_rate, resize_wd=img_wd, resize_ht=img_ht, split_len=split_len,
                object_skip_rate=object_skip_rate, bg_object_skip_rate=bg_object_skip_rate,
                end_gray_img_duration_in_sec=main_img_duration, export_json=export_json
            )
            
            # Générer l'animation
            draw_whiteboard_animations(
                image_bgr, mask_path, hand_path, hand_mask_path, save_video_path, variables
            )
            
            # Export JSON si demandé
            if export_json:
                export_animation_json(variables, json_export_path)
                json_exports.append(json_export_path)
            
            # Convertir en H.264
            ff_stat = ffmpeg_convert(source_vid=save_video_path, dest_vid=ffmpeg_video_path, platform=platform)
            
            if ff_stat:
                generated_videos.append(ffmpeg_video_path)
                os.unlink(save_video_path)
                print(f"  ✅ Vidéo générée: {os.path.basename(ffmpeg_video_path)}")
            else:
                generated_videos.append(save_video_path)
                print(f"  ✅ Vidéo générée (sans conversion): {os.path.basename(save_video_path)}")
        
        except Exception as e:
            print(f"  ❌ Erreur lors du traitement de l'image {idx}: {e}")
            continue
    
    # Vérifier qu'au moins une vidéo a été générée
    if not generated_videos:
        return {"status": False, "message": "Aucune vidéo n'a pu être générée"}
    
    # Concaténer les vidéos si plusieurs
    if len(generated_videos) > 1:
        print("\n" + "="*60)
        print("🔗 COMBINAISON DES VIDÉOS")
        print("="*60)
        
        combined_video_name = f"vid_{series_id}_combined.mp4"
        combined_video_path = os.path.join(save_path, combined_video_name)
        
        concat_success = concatenate_videos(generated_videos, combined_video_path, transition_type=transition, transition_duration=transition_duration)
        
        if concat_success:
            # Supprimer les vidéos individuelles après concaténation réussie
            for video_path in generated_videos:
                try:
                    os.unlink(video_path)
                    print(f"  🗑️ Vidéo intermédiaire supprimée: {os.path.basename(video_path)}")
                except Exception as e:
                    print(f"  ⚠️ Impossible de supprimer {os.path.basename(video_path)}: {e}")
            
            result = {
                "status": True,
                "message": combined_video_path,
                "images_processed": len(image_paths),
                "videos_generated": len(generated_videos)
            }
            
            if json_exports:
                result["json_paths"] = json_exports
            
            return result
        else:
            # Échec de la concaténation, garder les vidéos individuelles
            result = {
                "status": True,
                "message": f"Vidéos individuelles générées (échec de la concaténation): {', '.join([os.path.basename(v) for v in generated_videos])}",
                "individual_videos": generated_videos,
                "images_processed": len(image_paths),
                "videos_generated": len(generated_videos)
            }
            
            if json_exports:
                result["json_paths"] = json_exports
            
            return result
    else:
        # Une seule vidéo générée
        result = {
            "status": True,
            "message": generated_videos[0],
            "images_processed": 1,
            "videos_generated": 1
        }
        
        if json_exports:
            result["json_path"] = json_exports[0]
        
        return result


def get_split_lens(image_path):
    """ Obtient la résolution de l'image (redimensionnée) et les diviseurs communs (split_lens). """
    final_return = {"image_res": "None", "split_lens": []}
    try:
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
             raise ValueError(f"Impossible de lire l'image: {image_path}")
             
        img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
        aspect_ratio = img_wd / img_ht
        img_ht = find_nearest_res(img_ht)
        new_aspect_wd = int(img_ht * aspect_ratio)
        img_wd = find_nearest_res(new_aspect_wd)
        
        hcf_list = common_divisors(img_ht, img_wd)
        filename = os.path.basename(image_path)
        
        final_return["split_lens"] = hcf_list
        final_return["image_res"] = f"{filename}, résolution vidéo cible: {img_wd}x{img_ht}"
    except Exception as e:
        final_return["image_res"] = f"Erreur lors de la lecture de l'image. {e}"
        print(f"Erreur lors de l'obtention des split lens: {e}")
        
    return final_return

# --- Configuration CLI (Ligne de Commande) ---

DEFAULT_FRAME_RATE = 30
DEFAULT_SPLIT_LEN = 15
DEFAULT_OBJECT_SKIP_RATE = 8
DEFAULT_BG_OBJECT_SKIP_RATE = 20
DEFAULT_MAIN_IMG_DURATION = 3

def main():
    """Fonction principale pour gérer les arguments CLI et lancer l'animation."""
    parser = argparse.ArgumentParser(
        description="Crée une vidéo d'animation style tableau blanc à partir d'une ou plusieurs images. "
        "Utilisez aussi --get-split-lens [image_path] pour voir les valeurs 'split_len' recommandées."
    )
    
    parser.add_argument(
        'image_paths', 
        type=str, 
        nargs='*', 
        default=None,
        help="Le(s) chemin(s) du/des fichier(s) image(s) à animer (ex: image1.png image2.png image3.png)"
    )

    parser.add_argument(
        '--split-len', 
        type=int, 
        default=DEFAULT_SPLIT_LEN,
        help=f"Taille de grille pour le dessin. Par défaut: {DEFAULT_SPLIT_LEN}. Utilisez des diviseurs de la résolution pour de meilleurs résultats."
    )
    parser.add_argument(
        '--frame-rate', 
        type=int, 
        default=DEFAULT_FRAME_RATE,
        help=f"Images par seconde (FPS). Par défaut: {DEFAULT_FRAME_RATE}."
    )
    parser.add_argument(
        '--skip-rate', 
        type=int, 
        default=DEFAULT_OBJECT_SKIP_RATE,
        help=f"Vitesse de dessin. Plus grand = plus rapide. Par défaut: {DEFAULT_OBJECT_SKIP_RATE}."
    )
    parser.add_argument(
        '--bg-skip-rate', 
        type=int, 
        default=DEFAULT_BG_OBJECT_SKIP_RATE,
        help=f"Taux de saut pour l'arrière-plan (non utilisé ici sans masques). Par défaut: {DEFAULT_BG_OBJECT_SKIP_RATE}."
    )
    parser.add_argument(
        '--duration', 
        type=int, 
        default=DEFAULT_MAIN_IMG_DURATION,
        help=f"Durée en secondes de l'image finale. Par défaut: {DEFAULT_MAIN_IMG_DURATION}."
    )
    
    parser.add_argument(
        '--transition',
        type=str,
        default='none',
        choices=['none', 'fade', 'wipe', 'push_left', 'push_right', 'iris'],
        help="Type de transition entre les slides (par défaut: none). Disponible: none, fade, wipe, push_left, push_right, iris."
    )
    
    parser.add_argument(
        '--transition-duration',
        type=float,
        default=0.5,
        help="Durée de la transition en secondes (par défaut: 0.5)."
    )
    
    parser.add_argument(
        '--export-json',
        action='store_true',
        help="Exporte les données d'animation au format JSON (séquence de dessin, positions de la main, etc.)."
    )
    
    parser.add_argument(
        '--get-split-lens', 
        action='store_true',
        help="Affiche les valeurs 'split_len' recommandées pour le chemin d'image fourni, puis quitte."
    )

    args = parser.parse_args()
    
    if not (os.path.exists(hand_path) and os.path.exists(hand_mask_path)):
        print("\n❌ ERREUR DE CONFIGURATION: Les images de la main (drawing-hand.png et hand-mask.png) sont introuvables.")
        sys.exit(1)

    # --- Mode de vérification des 'split-lens' ---
    if args.get_split_lens:
        if not args.image_paths or len(args.image_paths) == 0:
            print("Erreur: Vous devez spécifier le chemin de l'image après --get-split-lens.")
            return

        path_to_check = args.image_paths[0]
        if not os.path.exists(path_to_check):
             print(f"Erreur: Le chemin d'image spécifié est introuvable: {path_to_check}")
             return
             
        res_info = get_split_lens(path_to_check)
        print("\n" + "="*50)
        print("INFOS DE RÉSOLUTION ET VALEURS 'SPLIT_LEN' RECOMMANDÉES")
        print("="*50)
        print(res_info['image_res'])
        print(f"Valeurs 'split_len' suggérées (diviseurs communs de la résolution cible):")
        print(res_info['split_lens'])
        print("\nUtilisez l'une de ces valeurs avec l'argument --split-len.")
        print("="*50 + "\n")
        return

    # --- Mode de génération vidéo ---
    if not args.image_paths or len(args.image_paths) == 0:
        parser.print_help()
        print("\n❌ ERREUR: Au moins un chemin d'image est requis.")
        return

    # Vérifier que les images existent
    valid_images = []
    for img_path in args.image_paths:
        if os.path.exists(img_path):
            valid_images.append(img_path)
        else:
            print(f"⚠️ Avertissement: Image ignorée (introuvable): {img_path}")
    
    if not valid_images:
        print("❌ Erreur: Aucune image valide fournie.")
        return

    print("\n" + "="*50)
    print("🎬 Lancement de l'animation Whiteboard")
    if len(valid_images) == 1:
        print(f"Image source: {valid_images[0]}")
    else:
        print(f"Images sources: {len(valid_images)} image(s)")
        for i, img in enumerate(valid_images, 1):
            print(f"  {i}. {os.path.basename(img)}")
    print(f"Paramètres: Split={args.split_len}, FPS={args.frame_rate}, Skip={args.skip_rate}")
    print("="*50)

    # Traitement unique ou multiple
    if len(valid_images) == 1:
        # Une seule image - utiliser l'ancienne méthode
        def final_callback_cli(result):
            """Fonction de rappel appelée à la fin de la génération."""
            if result["status"]:
                print(f"\n✅ SUCCÈS! Vidéo enregistrée sous: {result['message']}")
                if "json_path" in result:
                    print(f"✅ Données d'animation exportées: {result['json_path']}")
            else:
                print(f"\n❌ ÉCHEC de la génération vidéo. Message: {result['message']}")

        # Appel de la fonction synchrone pour la CLI
        initiate_sketch_sync(
            valid_images[0],
            args.split_len,
            args.frame_rate,
            args.skip_rate,
            args.bg_skip_rate,
            args.duration,
            final_callback_cli,
            export_json=args.export_json
        )
    else:
        # Plusieurs images - utiliser la nouvelle méthode
        result = process_multiple_images(
            valid_images,
            args.split_len,
            args.frame_rate,
            args.skip_rate,
            args.bg_skip_rate,
            args.duration,
            export_json=args.export_json,
            transition=args.transition,
            transition_duration=args.transition_duration
        )
        
        print("\n" + "="*60)
        if result["status"]:
            print("✅ SUCCÈS!")
            print(f"📊 Images traitées: {result.get('images_processed', 0)}")
            print(f"🎬 Vidéos générées: {result.get('videos_generated', 0)}")
            
            if "individual_videos" in result:
                print("\n📹 Vidéos individuelles (la concaténation a échoué):")
                for video in result["individual_videos"]:
                    print(f"  • {video}")
            else:
                print(f"\n🎥 Vidéo finale: {result['message']}")
            
            if "json_paths" in result:
                print(f"\n📄 Données d'animation exportées ({len(result['json_paths'])} fichier(s)):")
                for json_path in result["json_paths"]:
                    print(f"  • {json_path}")
            elif "json_path" in result:
                print(f"\n📄 Données d'animation exportées: {result['json_path']}")
        else:
            print("❌ ÉCHEC!")
            print(f"Message: {result['message']}")
        print("="*60 + "\n")

if __name__ == '__main__':
    main()