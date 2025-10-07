#!/usr/bin/env python3
"""
Exemple d'utilisation des données d'animation exportées en JSON.

Ce script démontre comment charger et utiliser les données d'animation
pour recréer ou analyser l'animation dans d'autres applications.
"""

import json
import sys

def load_animation_data(json_path):
    """Charge les données d'animation depuis un fichier JSON."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de décodage JSON: {e}")
        sys.exit(1)

def print_animation_summary(data):
    """Affiche un résumé des données d'animation."""
    metadata = data['metadata']
    frames = data['animation']['frames_written']
    
    print("\n" + "="*60)
    print("RÉSUMÉ DE L'ANIMATION")
    print("="*60)
    
    print(f"\n📊 Métadonnées:")
    print(f"  • Résolution: {metadata['width']}x{metadata['height']}")
    print(f"  • FPS: {metadata['frame_rate']}")
    print(f"  • Taille de grille: {metadata['split_len']}")
    print(f"  • Taux de saut: {metadata['object_skip_rate']}")
    print(f"  • Nombre total de frames: {metadata['total_frames']}")
    print(f"  • Dimensions de la main: {metadata['hand_dimensions']['width']}x{metadata['hand_dimensions']['height']}")
    
    print(f"\n🎬 Séquence de dessin:")
    print(f"  • Frames enregistrées: {len(frames)}")
    if frames:
        first_frame = frames[0]
        last_frame = frames[-1]
        print(f"  • Première tuile dessinée: position grille {first_frame['tile_drawn']['grid_position']}")
        print(f"  • Dernière tuile dessinée: position grille {last_frame['tile_drawn']['grid_position']}")
        
        # Calculer la durée de l'animation
        duration = len(frames) / metadata['frame_rate']
        print(f"  • Durée estimée du dessin: {duration:.2f} secondes")
    
    print("\n" + "="*60)

def analyze_drawing_path(data):
    """Analyse le chemin de dessin et affiche des statistiques."""
    frames = data['animation']['frames_written']
    metadata = data['metadata']
    
    print("\n" + "="*60)
    print("ANALYSE DU CHEMIN DE DESSIN")
    print("="*60)
    
    if not frames:
        print("Aucune frame à analyser.")
        return
    
    # Calculer la distance totale parcourue par la main
    total_distance = 0
    for i in range(1, len(frames)):
        prev_pos = frames[i-1]['hand_position']
        curr_pos = frames[i]['hand_position']
        
        dx = curr_pos['x'] - prev_pos['x']
        dy = curr_pos['y'] - prev_pos['y']
        distance = (dx**2 + dy**2) ** 0.5
        total_distance += distance
    
    print(f"\n📏 Distance totale parcourue par la main: {total_distance:.2f} pixels")
    print(f"📏 Distance moyenne entre frames: {total_distance / (len(frames) - 1):.2f} pixels")
    
    # Calculer les limites du mouvement de la main
    x_positions = [f['hand_position']['x'] for f in frames]
    y_positions = [f['hand_position']['y'] for f in frames]
    
    print(f"\n📍 Zone de dessin:")
    print(f"  • X: {min(x_positions)} → {max(x_positions)} (étendue: {max(x_positions) - min(x_positions)} pixels)")
    print(f"  • Y: {min(y_positions)} → {max(y_positions)} (étendue: {max(y_positions) - min(y_positions)} pixels)")
    
    print("\n" + "="*60)

def export_drawing_sequence(data, output_file):
    """Exporte la séquence de dessin dans un format simplifié."""
    frames = data['animation']['frames_written']
    
    sequence = []
    for frame in frames:
        sequence.append({
            'frame': frame['frame_number'],
            'position': frame['hand_position'],
            'tile': frame['tile_drawn']['grid_position']
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sequence, f, indent=2)
    
    print(f"\n✅ Séquence de dessin exportée vers: {output_file}")

def main():
    """Fonction principale."""
    if len(sys.argv) < 2:
        print("Usage: python use_animation_data.py <animation.json> [--export-sequence output.json]")
        sys.exit(1)
    
    json_path = sys.argv[1]
    
    # Charger les données
    print(f"📂 Chargement de: {json_path}")
    data = load_animation_data(json_path)
    
    # Afficher le résumé
    print_animation_summary(data)
    
    # Analyser le chemin
    analyze_drawing_path(data)
    
    # Exporter la séquence si demandé
    if len(sys.argv) > 3 and sys.argv[2] == '--export-sequence':
        output_file = sys.argv[3]
        export_drawing_sequence(data, output_file)
    
    print("\n✨ Analyse terminée!\n")

if __name__ == '__main__':
    main()
