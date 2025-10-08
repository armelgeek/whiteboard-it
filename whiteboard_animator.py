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

# Default values for video generation
DEFAULT_FRAME_RATE = 30
DEFAULT_SPLIT_LEN = 15
DEFAULT_OBJECT_SKIP_RATE = 8
DEFAULT_BG_OBJECT_SKIP_RATE = 20
DEFAULT_MAIN_IMG_DURATION = 3
DEFAULT_CRF = 18  # Lower = better quality (0-51, 18 is visually lossless)

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
            # Apply watermark if specified
            if variables.watermark_path:
                drawn_frame_with_hand = apply_watermark(
                    drawn_frame_with_hand,
                    variables.watermark_path,
                    variables.watermark_position,
                    variables.watermark_opacity,
                    variables.watermark_scale
                )
            
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
        final_frame = variables.img.copy()
        # Apply watermark if specified
        if variables.watermark_path:
            final_frame = apply_watermark(
                final_frame,
                variables.watermark_path,
                variables.watermark_position,
                variables.watermark_opacity,
                variables.watermark_scale
            )
        variables.video_object.write(final_frame)

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


def calculate_aspect_ratio_dimensions(original_width, original_height, aspect_ratio):
    """Calculate dimensions for a specific aspect ratio.
    
    Args:
        original_width: Original image width
        original_height: Original image height
        aspect_ratio: Target aspect ratio string ('1:1', '16:9', '9:16', 'original')
    
    Returns:
        tuple: (width, height) for the target aspect ratio
    """
    if aspect_ratio == 'original':
        return original_width, original_height
    
    # Parse aspect ratio
    if aspect_ratio == '1:1':
        ratio_w, ratio_h = 1, 1
    elif aspect_ratio == '16:9':
        ratio_w, ratio_h = 16, 9
    elif aspect_ratio == '9:16':
        ratio_w, ratio_h = 9, 16
    else:
        return original_width, original_height
    
    # Calculate dimensions maintaining the aspect ratio
    target_ratio = ratio_w / ratio_h
    original_ratio = original_width / original_height
    
    # Determine base dimension (use the larger dimension as reference)
    if aspect_ratio == '1:1':
        # For 1:1, use the smaller dimension to avoid too much cropping
        base = min(original_width, original_height)
        width = height = find_nearest_res(base)
    elif aspect_ratio == '16:9':
        # HD 16:9 resolutions
        if original_height >= 1080:
            width, height = 1920, 1080
        elif original_height >= 720:
            width, height = 1280, 720
        else:
            height = find_nearest_res(original_height)
            width = find_nearest_res(int(height * target_ratio))
    elif aspect_ratio == '9:16':
        # Vertical video resolutions
        if original_width >= 1080:
            width, height = 1080, 1920
        elif original_width >= 720:
            width, height = 720, 1280
        else:
            width = find_nearest_res(original_width)
            height = find_nearest_res(int(width / target_ratio))
    else:
        width, height = original_width, original_height
    
    return width, height


def apply_aspect_ratio_padding(image, target_width, target_height):
    """Apply padding to maintain aspect ratio with letterboxing/pillarboxing.
    
    Args:
        image: Input image (numpy array)
        target_width: Target width
        target_height: Target height
    
    Returns:
        Padded image with white background
    """
    img_height, img_width = image.shape[:2]
    
    # Calculate scaling to fit within target dimensions
    scale = min(target_width / img_width, target_height / img_height)
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    # Resize image
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    # Create white canvas
    canvas = np.ones((target_height, target_width, 3), dtype=np.uint8) * 255
    
    # Calculate position to center the image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    # Place image on canvas
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized
    
    return canvas


def apply_watermark(frame, watermark_path, position='bottom-right', opacity=0.5, scale=0.1):
    """Apply watermark to a frame.
    
    Args:
        frame: Input frame (numpy array)
        watermark_path: Path to watermark image
        position: Position string ('top-left', 'top-right', 'bottom-left', 'bottom-right', 'center')
        opacity: Watermark opacity (0.0 to 1.0)
        scale: Scale of watermark relative to frame width (0.0 to 1.0)
    
    Returns:
        Frame with watermark applied
    """
    if not watermark_path or not os.path.exists(watermark_path):
        return frame
    
    try:
        # Load watermark
        watermark = cv2.imread(watermark_path, cv2.IMREAD_UNCHANGED)
        if watermark is None:
            print(f"⚠️ Warning: Could not load watermark from {watermark_path}")
            return frame
        
        # Calculate watermark size
        frame_height, frame_width = frame.shape[:2]
        watermark_width = int(frame_width * scale)
        watermark_height = int(watermark.shape[0] * (watermark_width / watermark.shape[1]))
        watermark_resized = cv2.resize(watermark, (watermark_width, watermark_height))
        
        # Handle alpha channel
        if watermark_resized.shape[2] == 4:
            # Has alpha channel
            watermark_bgr = watermark_resized[:, :, :3]
            watermark_alpha = watermark_resized[:, :, 3] / 255.0 * opacity
        else:
            # No alpha channel, use opacity
            watermark_bgr = watermark_resized
            watermark_alpha = np.ones((watermark_height, watermark_width)) * opacity
        
        # Calculate position
        margin = 20
        if position == 'top-left':
            y1, y2 = margin, margin + watermark_height
            x1, x2 = margin, margin + watermark_width
        elif position == 'top-right':
            y1, y2 = margin, margin + watermark_height
            x1, x2 = frame_width - watermark_width - margin, frame_width - margin
        elif position == 'bottom-left':
            y1, y2 = frame_height - watermark_height - margin, frame_height - margin
            x1, x2 = margin, margin + watermark_width
        elif position == 'bottom-right':
            y1, y2 = frame_height - watermark_height - margin, frame_height - margin
            x1, x2 = frame_width - watermark_width - margin, frame_width - margin
        elif position == 'center':
            y1, y2 = (frame_height - watermark_height) // 2, (frame_height + watermark_height) // 2
            x1, x2 = (frame_width - watermark_width) // 2, (frame_width + watermark_width) // 2
        else:
            # Default to bottom-right
            y1, y2 = frame_height - watermark_height - margin, frame_height - margin
            x1, x2 = frame_width - watermark_width - margin, frame_width - margin
        
        # Ensure bounds are within frame
        y1, y2 = max(0, y1), min(frame_height, y2)
        x1, x2 = max(0, x1), min(frame_width, x2)
        
        # Adjust watermark size if it doesn't fit
        actual_height = y2 - y1
        actual_width = x2 - x1
        if actual_height != watermark_height or actual_width != watermark_width:
            watermark_bgr = watermark_bgr[:actual_height, :actual_width]
            watermark_alpha = watermark_alpha[:actual_height, :actual_width]
        
        # Apply watermark using alpha blending
        roi = frame[y1:y2, x1:x2]
        for c in range(3):
            roi[:, :, c] = roi[:, :, c] * (1 - watermark_alpha) + watermark_bgr[:, :, c] * watermark_alpha
        
        frame[y1:y2, x1:x2] = roi
        
    except Exception as e:
        print(f"⚠️ Warning: Error applying watermark: {e}")
    
    return frame

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
        watermark_path=None,
        watermark_position='bottom-right',
        watermark_opacity=0.5,
        watermark_scale=0.1,
    ):
        self.frame_rate = frame_rate
        self.resize_wd = resize_wd
        self.resize_ht = resize_ht
        self.split_len = split_len
        self.object_skip_rate = object_skip_rate
        self.bg_object_skip_rate = bg_object_skip_rate
        self.end_gray_img_duration_in_sec = end_gray_img_duration_in_sec
        self.export_json = export_json
        self.watermark_path = watermark_path
        self.watermark_position = watermark_position
        self.watermark_opacity = watermark_opacity
        self.watermark_scale = watermark_scale
        
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


def ffmpeg_convert(source_vid, dest_vid, platform="linux", crf=18):
    """Convertit la vidéo brute (mp4v) en H.264 compatible avec PyAV.
    
    Args:
        source_vid: Chemin de la vidéo source
        dest_vid: Chemin de la vidéo de destination
        platform: Plateforme cible
        crf: Constant Rate Factor (0-51, lower = better quality, 18 is visually lossless)
    """
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
        out_stream.options = {"crf": str(crf)}

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


def concatenate_videos(video_paths, output_path, transition_type='none', transition_duration=0.5, per_slide_transitions=None, crf=18):
    """Concatène plusieurs vidéos en une seule vidéo finale avec transitions optionnelles.
    
    Args:
        video_paths: Liste des chemins des vidéos à concaténer
        output_path: Chemin de sortie pour la vidéo combinée
        transition_type: Type de transition par défaut ('none', 'fade', 'wipe', 'push_left', 'push_right', 'iris')
        transition_duration: Durée de la transition en secondes (par défaut)
        per_slide_transitions: Liste de dicts avec configs de transition par slide
        crf: Constant Rate Factor for video quality (0-51, lower = better quality)
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
        out_stream.options = {"crf": str(crf)}
        
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
                
                # Déterminer le type et la durée de transition pour cette slide
                current_transition_type = transition_type
                current_transition_duration = transition_duration
                
                # Si une configuration par slide existe, l'utiliser
                if per_slide_transitions and i - 1 < len(per_slide_transitions):
                    slide_trans_config = per_slide_transitions[i - 1]
                    if 'type' in slide_trans_config:
                        current_transition_type = slide_trans_config['type']
                    if 'duration' in slide_trans_config:
                        current_transition_duration = slide_trans_config['duration']
                
                # Calculer le nombre de frames pour cette transition
                current_num_transition_frames = int(float(fps) * current_transition_duration)
                
                # Ajouter des frames de pause avant la transition si spécifié
                pause_duration = 0
                if per_slide_transitions and i - 1 < len(per_slide_transitions):
                    pause_duration = per_slide_transitions[i - 1].get('pause_before', 0)
                
                if pause_duration > 0:
                    num_pause_frames = int(float(fps) * pause_duration)
                    print(f"    Ajout d'une pause de {pause_duration}s ({num_pause_frames} frames)")
                    last_frame_np = last_frame.to_ndarray(format='bgr24')
                    if last_frame_np.shape[:2] != (height, width):
                        last_frame_np = cv2.resize(last_frame_np, (width, height))
                    
                    for _ in range(num_pause_frames):
                        av_frame = av.VideoFrame.from_ndarray(last_frame_np, format='bgr24')
                        av_frame.pts = None
                        packets = out_stream.encode(av_frame)
                        for packet in packets:
                            output_container.mux(packet)
                
                # Afficher la transition utilisée
                if current_transition_type != 'none':
                    print(f"    Transition: {current_transition_type} ({current_transition_duration}s)")
                
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
                    last_frame_np, first_frame_np, current_transition_type, 
                    current_num_transition_frames, float(fps)
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


def initiate_sketch_sync(image_path, split_len, frame_rate, object_skip_rate, bg_object_skip_rate, main_img_duration, callback, save_path=save_path, which_platform="linux", export_json=False, aspect_ratio='original', crf=DEFAULT_CRF, watermark_path=None, watermark_position='bottom-right', watermark_opacity=0.5, watermark_scale=0.1):
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

        # Calculate dimensions based on aspect ratio
        img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
        
        if aspect_ratio != 'original':
            img_wd, img_ht = calculate_aspect_ratio_dimensions(img_wd, img_ht, aspect_ratio)
            print(f"Ratio d'aspect: {aspect_ratio}, Résolution cible: {img_wd}x{img_ht}")
            # Apply padding to maintain aspect ratio
            image_bgr = apply_aspect_ratio_padding(image_bgr, img_wd, img_ht)
        else:
            original_aspect_ratio = img_wd / img_ht
            img_ht = find_nearest_res(img_ht)
            new_aspect_wd = int(img_ht * original_aspect_ratio)
            img_wd = find_nearest_res(new_aspect_wd)
            print(f"Résolution cible: {img_wd}x{img_ht}")

        variables = AllVariables(
            frame_rate=frame_rate, resize_wd=img_wd, resize_ht=img_ht, split_len=split_len, 
            object_skip_rate=object_skip_rate, bg_object_skip_rate=bg_object_skip_rate, 
            end_gray_img_duration_in_sec=main_img_duration, export_json=export_json,
            watermark_path=watermark_path, watermark_position=watermark_position,
            watermark_opacity=watermark_opacity, watermark_scale=watermark_scale
        )

        draw_whiteboard_animations(
            image_bgr, mask_path, hand_path, hand_mask_path, save_video_path, variables
        )
        
        # Export JSON if requested
        if export_json:
            export_animation_json(variables, json_export_path)
        
        ff_stat = ffmpeg_convert(source_vid=save_video_path, dest_vid=ffmpeg_video_path, platform=platform, crf=crf)
        
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


def process_multiple_images(image_paths, split_len, frame_rate, object_skip_rate, bg_object_skip_rate, main_img_duration, which_platform="linux", export_json=False, transition='none', transition_duration=0.5, per_slide_config=None, aspect_ratio='original', crf=DEFAULT_CRF, watermark_path=None, watermark_position='bottom-right', watermark_opacity=0.5, watermark_scale=0.1):
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
        per_slide_config: Configuration par slide (dict avec clés 'slides' et 'transitions')
        aspect_ratio: Target aspect ratio ('original', '1:1', '16:9', '9:16')
        crf: Video quality (0-51, lower = better quality)
        watermark_path: Path to watermark image
        watermark_position: Position of watermark
        watermark_opacity: Opacity of watermark (0.0-1.0)
        watermark_scale: Scale of watermark relative to frame width
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
    
    # Préparer les configurations de transition par slide
    transition_configs = []
    
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
            
            # Calculer la résolution basée sur le ratio d'aspect
            img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
            
            if aspect_ratio != 'original':
                img_wd, img_ht = calculate_aspect_ratio_dimensions(img_wd, img_ht, aspect_ratio)
                print(f"  Ratio d'aspect: {aspect_ratio}, Résolution cible: {img_wd}x{img_ht}")
                # Apply padding to maintain aspect ratio
                image_bgr = apply_aspect_ratio_padding(image_bgr, img_wd, img_ht)
            else:
                original_aspect_ratio = img_wd / img_ht
                img_ht = find_nearest_res(img_ht)
                new_aspect_wd = int(img_ht * original_aspect_ratio)
                img_wd = find_nearest_res(new_aspect_wd)
                print(f"  Résolution cible: {img_wd}x{img_ht}")
            
            # Obtenir la configuration pour cette slide
            slide_config = {}
            if per_slide_config and 'slides' in per_slide_config:
                # Chercher la config pour cette slide (index 0-based dans le config)
                for slide_cfg in per_slide_config['slides']:
                    if slide_cfg.get('index') == idx - 1:
                        slide_config = slide_cfg
                        break
            
            # Utiliser les paramètres de la slide ou les valeurs par défaut
            slide_skip_rate = slide_config.get('skip_rate', object_skip_rate)
            slide_duration = slide_config.get('duration', main_img_duration)
            
            # Pour les slides intermédiaires (pas la dernière), vérifier si une durée est spécifiée
            is_last_image = (idx == len(image_paths))
            if not is_last_image and 'duration' not in slide_config:
                # Si pas de durée spécifiée pour slide intermédiaire, utiliser 0
                slide_duration = 0
            
            print(f"  Vitesse de dessin (skip-rate): {slide_skip_rate}")
            print(f"  Durée de la slide: {slide_duration}s")
            
            # Stocker la config de transition pour plus tard
            transition_config = {}
            if per_slide_config and 'transitions' in per_slide_config:
                # Chercher la config de transition après cette slide
                for trans_cfg in per_slide_config['transitions']:
                    if trans_cfg.get('after_slide') == idx - 1:
                        transition_config = trans_cfg
                        break
            transition_configs.append(transition_config)
            
            # Créer les variables
            variables = AllVariables(
                frame_rate=frame_rate, resize_wd=img_wd, resize_ht=img_ht, split_len=split_len,
                object_skip_rate=slide_skip_rate, bg_object_skip_rate=bg_object_skip_rate,
                end_gray_img_duration_in_sec=slide_duration, export_json=export_json,
                watermark_path=watermark_path, watermark_position=watermark_position,
                watermark_opacity=watermark_opacity, watermark_scale=watermark_scale
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
            ff_stat = ffmpeg_convert(source_vid=save_video_path, dest_vid=ffmpeg_video_path, platform=platform, crf=crf)
            
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
        
        concat_success = concatenate_videos(
            generated_videos, 
            combined_video_path, 
            transition_type=transition, 
            transition_duration=transition_duration,
            per_slide_transitions=transition_configs,
            crf=crf
        )
        
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
                "message": "Vidéos individuelles générées (échec de la concaténation): " + ", ".join([os.path.basename(v) for v in generated_videos]),
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
        '--config',
        type=str,
        default=None,
        help="Chemin vers un fichier JSON pour une configuration personnalisée par slide (durée, vitesse, transitions, etc.)."
    )
    
    parser.add_argument(
        '--export-json',
        action='store_true',
        help="Exporte les données d'animation au format JSON (séquence de dessin, positions de la main, etc.)."
    )
    
    parser.add_argument(
        '--aspect-ratio',
        type=str,
        default='original',
        choices=['original', '1:1', '16:9', '9:16'],
        help="Ratio d'aspect de la vidéo (par défaut: original). Choix: original, 1:1, 16:9, 9:16."
    )
    
    parser.add_argument(
        '--quality',
        type=int,
        default=DEFAULT_CRF,
        choices=range(0, 52),
        metavar='0-51',
        help=f"Qualité vidéo (CRF: 0-51, plus bas = meilleure qualité, par défaut: {DEFAULT_CRF}). Valeurs recommandées: 18 (visually lossless), 23 (high quality), 28 (medium)."
    )
    
    parser.add_argument(
        '--watermark',
        type=str,
        default=None,
        help="Chemin vers l'image de filigrane (watermark) à appliquer sur la vidéo."
    )
    
    parser.add_argument(
        '--watermark-position',
        type=str,
        default='bottom-right',
        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
        help="Position du filigrane (par défaut: bottom-right)."
    )
    
    parser.add_argument(
        '--watermark-opacity',
        type=float,
        default=0.5,
        help="Opacité du filigrane (0.0 à 1.0, par défaut: 0.5)."
    )
    
    parser.add_argument(
        '--watermark-scale',
        type=float,
        default=0.1,
        help="Échelle du filigrane par rapport à la largeur de la vidéo (0.0 à 1.0, par défaut: 0.1)."
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
    
    # Charger la configuration personnalisée si fournie
    per_slide_config = None
    if args.config:
        if not os.path.exists(args.config):
            print(f"❌ Erreur: Fichier de configuration introuvable: {args.config}")
            return
        
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                per_slide_config = json.load(f)
            print(f"✅ Configuration personnalisée chargée depuis: {args.config}")
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du fichier de configuration: {e}")
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
    print(f"Ratio d'aspect: {args.aspect_ratio}, Qualité (CRF): {args.quality}")
    if args.watermark:
        print(f"Filigrane: {args.watermark} ({args.watermark_position}, opacité: {args.watermark_opacity})")
    if per_slide_config:
        print("🔧 Configuration personnalisée par slide activée")
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
            export_json=args.export_json,
            aspect_ratio=args.aspect_ratio,
            crf=args.quality,
            watermark_path=args.watermark,
            watermark_position=args.watermark_position,
            watermark_opacity=args.watermark_opacity,
            watermark_scale=args.watermark_scale
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
            transition_duration=args.transition_duration,
            per_slide_config=per_slide_config,
            aspect_ratio=args.aspect_ratio,
            crf=args.quality,
            watermark_path=args.watermark,
            watermark_position=args.watermark_position,
            watermark_opacity=args.watermark_opacity,
            watermark_scale=args.watermark_scale
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