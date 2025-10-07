# Exemples d'utilisation

Ce répertoire contient des exemples de scripts pour utiliser les données d'animation exportées.

## use_animation_data.py

Script Python qui démontre comment charger et analyser les données d'animation exportées en JSON.

### Utilisation

```bash
# Analyser un fichier d'animation
python use_animation_data.py animation.json

# Analyser et exporter une séquence simplifiée
python use_animation_data.py animation.json --export-sequence sequence.json
```

### Fonctionnalités

- **Résumé de l'animation** : Affiche les métadonnées (résolution, FPS, etc.)
- **Analyse du chemin** : Calcule la distance parcourue par la main
- **Export de séquence** : Exporte une version simplifiée de la séquence de dessin

### Exemple de sortie

```
============================================================
RÉSUMÉ DE L'ANIMATION
============================================================

📊 Métadonnées:
  • Résolution: 720x640
  • FPS: 30
  • Taille de grille: 15
  • Taux de saut: 10
  • Nombre total de frames: 19
  • Dimensions de la main: 284x467

🎬 Séquence de dessin:
  • Frames enregistrées: 19
  • Première tuile dessinée: position grille [9, 7]
  • Dernière tuile dessinée: position grille [21, 36]
  • Durée estimée du dessin: 0.63 secondes

============================================================

============================================================
ANALYSE DU CHEMIN DE DESSIN
============================================================

📏 Distance totale parcourue par la main: 2123.45 pixels
📏 Distance moyenne entre frames: 117.97 pixels

📍 Zone de dessin:
  • X: 97 → 547 (étendue: 450 pixels)
  • Y: 112 → 487 (étendue: 375 pixels)

============================================================
```

## Créer vos propres scripts

Vous pouvez créer vos propres scripts pour utiliser les données d'animation. Voici un exemple simple :

```python
import json

# Charger les données
with open('animation.json', 'r') as f:
    data = json.load(f)

# Accéder aux métadonnées
width = data['metadata']['width']
height = data['metadata']['height']

# Parcourir les frames
for frame in data['animation']['frames_written']:
    x = frame['hand_position']['x']
    y = frame['hand_position']['y']
    print(f"Frame {frame['frame_number']}: Main à ({x}, {y})")
```

## Cas d'utilisation

Les données d'animation exportées peuvent être utilisées pour :

1. **Recréer l'animation** dans d'autres logiciels (After Effects, Blender, etc.)
2. **Optimiser les paramètres** en analysant la séquence de dessin
3. **Créer des animations personnalisées** en modifiant la séquence
4. **Intégrer dans des applications web** avec Canvas ou WebGL
5. **Générer des animations procédurales** basées sur les données
