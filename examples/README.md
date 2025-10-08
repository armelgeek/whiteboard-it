# Exemples d'utilisation

Ce répertoire contient des exemples de fichiers de configuration et de scripts pour démontrer les différentes fonctionnalités de Whiteboard-It.

## Fichiers de configuration JSON

### Contrôles de caméra et animations

#### camera_zoom_basic.json
Exemple basique de zoom de caméra sur une couche unique.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/camera_zoom_basic.json --split-len 30
```
**Fonctionnalités démontrées:**
- Zoom statique de 1.5x centré sur l'image
- Configuration de base de la caméra

#### animation_zoom_in.json
Effet de zoom-in appliqué après le dessin de la couche.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/animation_zoom_in.json --split-len 30
```
**Fonctionnalités démontrées:**
- Animation de zoom progressif post-dessin
- Zoom de 1.0x à 1.8x sur 2 secondes

#### camera_and_animation.json
Combinaison de zoom de caméra statique et animation de zoom.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/camera_and_animation.json --split-len 30
```
**Fonctionnalités démontrées:**
- Zoom initial de 1.3x avec focus personnalisé
- Animation additionnelle de zoom de 1.3x à 2.5x
- Changement de point focal pendant le zoom

#### multi_layer_camera.json
Plusieurs couches avec différents réglages de caméra.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/multi_layer_camera.json --split-len 30
```
**Fonctionnalités démontrées:**
- Trois couches avec des paramètres de caméra individuels
- Focus différent pour chaque couche
- Animation de zoom finale sur la dernière couche

#### cinematic_reveal.json
Effet cinématique de révélation avec zoom-out.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/cinematic_reveal.json --split-len 30
```
**Fonctionnalités démontrées:**
- Commence avec un zoom important (2.0x)
- Zoom-out progressif pour révéler la scène complète
- Effet dramatique de découverte

#### multi_slide_camera.json
Plusieurs slides avec différents focus de caméra et transitions.
```bash
python whiteboard_animator.py demo/1.jpg demo/2.jpg --config examples/multi_slide_camera.json --split-len 30
```
**Fonctionnalités démontrées:**
- Deux slides avec focus différents
- Zoom-in sur chaque slide
- Transition fade entre les slides

## Scripts d'analyse

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

## Conseils d'utilisation

### Pour les exemples de caméra
1. **Commencez simple**: Testez d'abord `camera_zoom_basic.json` pour comprendre les bases
2. **Ajustez les paramètres**: Modifiez les valeurs de zoom et position selon vos besoins
3. **Expérimentez**: Combinez différentes techniques pour créer des effets uniques

### Performance
- Utilisez `--split-len 30` ou plus pour un traitement plus rapide
- Les zooms importants peuvent augmenter le temps de rendu
- Testez avec des images de résolution modérée avant de traiter en haute résolution

### Bonnes pratiques
- Gardez les zooms entre 1.0 et 3.0 pour de meilleurs résultats
- Utilisez des durées d'animation de 1-2 secondes pour un effet naturel
- Coordonnez les effets de zoom avec les transitions pour une fluidité optimale

## Cas d'utilisation

Les données d'animation exportées peuvent être utilisées pour :

1. **Recréer l'animation** dans d'autres logiciels (After Effects, Blender, etc.)
2. **Optimiser les paramètres** en analysant la séquence de dessin
3. **Créer des animations personnalisées** en modifiant la séquence
4. **Intégrer dans des applications web** avec Canvas ou WebGL
5. **Générer des animations procédurales** basées sur les données

## Documentation complète

- **Contrôles de caméra**: Voir [CAMERA_ANIMATION_GUIDE.md](../CAMERA_ANIMATION_GUIDE.md)
- **Format de configuration**: Voir [CONFIG_FORMAT.md](../CONFIG_FORMAT.md)
- **Guide des couches**: Voir [LAYERS_GUIDE.md](../LAYERS_GUIDE.md)
