# Exemples d'utilisation

Ce répertoire contient des exemples de fichiers de configuration et de scripts pour démontrer les différentes fonctionnalités de Whiteboard-It.

## 🚀 Guide de démarrage rapide

**Nouveau dans Whiteboard-It?** Consultez le **[Guide de référence rapide (QUICK_REFERENCE.md)](QUICK_REFERENCE.md)** pour:
- Exemples classés par niveau de difficulté (débutant à expert)
- Commandes prêtes à l'emploi
- Options de ligne de commande (qualité, formats, watermark)
- Combinaisons populaires pour réseaux sociaux

---

## Fichiers de configuration JSON

### 1. Concepts de base

#### basic_drawing.json
Exemple simple d'animation de dessin whiteboard avec une seule image.
```bash
python whiteboard_animator.py demo/1.jpg --config examples/basic_drawing.json --split-len 30
```
**Fonctionnalités démontrées:**
- Animation de dessin de base avec la main
- Configuration minimale (durée et vitesse de dessin)
- Idéal pour démarrer

#### multi_slide_transitions.json
Plusieurs slides avec différentes transitions entre elles.
```bash
python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png --config examples/multi_slide_transitions.json --split-len 30
```
**Fonctionnalités démontrées:**
- Trois slides avec des vitesses de dessin différentes
- Transition "fade" entre la slide 1 et 2
- Transition "iris" entre la slide 2 et 3
- Configuration personnalisée par slide

#### all_transitions.json
Démonstration de tous les types de transitions disponibles.
```bash
python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png demo/1.jpg demo/2.jpg demo/3.png --config examples/all_transitions.json --split-len 30
```
**Fonctionnalités démontrées:**
- Transition **fade** : Fondu enchaîné progressif
- Transition **wipe** : Balayage de gauche à droite
- Transition **push_left** : Pousse la slide vers la gauche
- Transition **push_right** : Pousse la slide vers la droite
- Transition **iris** : Cercle qui s'agrandit depuis le centre
- Six slides avec toutes les transitions

#### per_slide_config.json
Configuration avancée par slide avec durées et transitions personnalisées.
```bash
python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png --config examples/per_slide_config.json --split-len 30
```
**Fonctionnalités démontrées:**
- Durée différente pour chaque slide
- Vitesse de dessin différente pour chaque slide
- Pause avant transition
- Idéal pour créer des présentations dynamiques

### 2. Couches multiples (Layers)

#### layers_composition.json
Composition de plusieurs images sur une même slide avec positionnement et propriétés.
```bash
python whiteboard_animator.py demo/placeholder.png --config examples/layers_composition.json --split-len 30
```
**Fonctionnalités démontrées:**
- Trois images superposées sur la même slide
- Positionnement précis (x, y) de chaque couche
- Ordre de superposition (z-index)
- Échelle et opacité personnalisées pour chaque couche
- Vitesses de dessin différentes par couche

### 3. Animations avancées de couches

#### advanced_layer_modes.json
Différents modes d'animation pour les couches (draw, eraser, static).
```bash
python whiteboard_animator.py demo/placeholder.png --config examples/advanced_layer_modes.json --split-len 30
```
**Fonctionnalités démontrées:**
- **Mode draw** : Dessin normal avec la main (couche 1)
- **Mode eraser** : Animation avec une gomme (couche 2)
- **Mode static** : Apparition sans animation de dessin (couche 3)
- Animations d'entrée (fade_in, zoom_in)
- Animation de sortie (fade_out)

#### entrance_exit_animations.json
Démonstration complète des animations d'entrée et de sortie.
```bash
python whiteboard_animator.py demo/placeholder.png --config examples/entrance_exit_animations.json --split-len 30
```
**Fonctionnalités démontrées:**
- Animation d'entrée **fade_in** : Fondu depuis blanc
- Animation d'entrée **slide_in_left** : Glissement depuis la gauche
- Animation d'entrée **slide_in_bottom** : Glissement depuis le bas
- Animation de sortie **slide_out_top** : Glissement vers le haut
- Combinaison d'entrées et sorties sur une même couche
- Types disponibles: fade_in/out, slide_in/out (left/right/top/bottom), zoom_in/out

#### morphing_layers.json
Effet de morphing fluide entre deux couches consécutives.
```bash
python whiteboard_animator.py demo/placeholder.png --config examples/morphing_layers.json --split-len 30
```
**Fonctionnalités démontrées:**
- Transition morphing progressive entre deux images
- Interpolation automatique des pixels
- Durée personnalisable
- Idéal pour transitions entre contenus similaires

#### text_layer_example.json
✨ **NOUVEAU** : Démonstration des couches de texte avec animation handwriting.
```bash
python whiteboard_animator.py --config examples/text_layer_example.json --split-len 30
```
**Fonctionnalités démontrées:**
- **Couches de texte dynamiques** : Génération de texte à la volée (pas besoin d'images)
- **Support multi-ligne** : Utilisez `\n` pour sauter des lignes
- **Styles de police** : normal, bold, italic, bold_italic
- **Couleurs personnalisables** : RGB tuple ou hex (ex: "#FF0000")
- **Alignement** : left, center, right
- **Animation handwriting** : Le texte est "écrit" comme avec un stylo
- **Animations d'entrée/sortie** : Compatible avec fade_in, slide_in, etc.
- **Position personnalisée** : Placement précis du texte sur le canvas

**Configuration de texte:**
```json
{
  "type": "text",
  "z_index": 1,
  "skip_rate": 12,
  "text_config": {
    "text": "Mon texte\nMulti-ligne",
    "font": "DejaVuSans",
    "size": 48,
    "color": "#0066CC",
    "style": "bold",
    "line_height": 1.5,
    "align": "center"
  }
}
```

### 4. Contrôles de caméra et animations post-dessin

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

### 5. Showcase complet

#### complete_showcase.json
Exemple combinant plusieurs fonctionnalités avancées pour créer une animation riche.
```bash
python whiteboard_animator.py demo/placeholder.png demo/placeholder.png --config examples/complete_showcase.json --split-len 30
```
**Fonctionnalités démontrées:**
- Plusieurs slides avec layers multiples
- Contrôles de caméra (zoom et positionnement)
- Animations post-dessin (zoom progressif)
- Mode static avec animations d'entrée
- Transitions personnalisées entre slides
- Pauses avant transitions
- Configuration complexe pour vidéos professionnelles

## Aperçu rapide des concepts

### Concepts de base
- ✅ **Animation de dessin** : Effet whiteboard avec main qui dessine
- ✅ **Slides multiples** : Plusieurs images dessinées séquentiellement
- ✅ **Transitions** : Effets visuels entre slides (fade, wipe, push, iris)
- ✅ **Configuration par slide** : Durée, vitesse, transitions personnalisées

### Concepts avancés
- ✅ **Couches (Layers)** : Superposition d'images sur une même slide
- ✅ **z-index** : Ordre d'affichage des couches
- ✅ **Positionnement** : Placement précis (x, y) de chaque couche
- ✅ **Transformations** : Scale (échelle) et opacity (transparence)
- ✅ **Modes d'animation** : draw (dessin), eraser (gomme), static (statique)
- ✅ **Animations d'entrée/sortie** : fade, slide, zoom pour apparitions/disparitions
- ✅ **Morphing** : Transition fluide entre couches
- ✅ **Contrôles de caméra** : Zoom et focus sur zones spécifiques
- ✅ **Animations post-dessin** : Effets de zoom après le dessin

## Guide de démarrage

### Pour débuter (concepts de base)
1. **basic_drawing.json** - Commencez ici pour comprendre l'animation de base
2. **multi_slide_transitions.json** - Apprenez à enchaîner plusieurs images
3. **all_transitions.json** - Explorez tous les types de transitions

### Pour progresser (couches et compositions)
4. **layers_composition.json** - Découvrez la superposition d'images
5. **per_slide_config.json** - Personnalisez chaque slide individuellement

### Pour maîtriser (animations avancées)
6. **advanced_layer_modes.json** - Modes draw, eraser, static
7. **entrance_exit_animations.json** - Animations d'apparition/disparition
8. **morphing_layers.json** - Transitions fluides entre images
9. **camera_zoom_basic.json** - Contrôles de caméra de base
10. **complete_showcase.json** - Tous les concepts combinés

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

### Pour les exemples de base
1. **Commencez simple**: Testez d'abord `basic_drawing.json` pour comprendre les fondamentaux
2. **Expérimentez les transitions**: Utilisez `all_transitions.json` pour voir tous les effets
3. **Progressez graduellement**: Suivez le guide de démarrage ci-dessus

### Pour les couches multiples
1. **Planifiez votre composition**: Dessinez d'abord la structure de vos couches
2. **Utilisez le z-index**: Organisez l'ordre de superposition (1 = fond, 2+ = premier plan)
3. **Ajustez les vitesses**: Variez les skip_rate pour des effets dynamiques
4. **Jouez avec l'opacité**: Créez des effets de transparence pour des compositions subtiles

### Pour les animations avancées
1. **Testez les modes**: draw pour dessin normal, eraser pour effacer, static pour apparition instantanée
2. **Durées recommandées**: 
   - Entrance/Exit animations: 0.5-1.5 secondes
   - Morphing: 0.3-0.8 secondes
   - Animations de zoom: 1.0-2.5 secondes
3. **Combinez intelligemment**: static + entrance/exit pour logos, draw + morph pour transitions

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

### Vidéos éducatives
- Utilisez **basic_drawing.json** pour des explications simples
- Utilisez **layers_composition.json** pour des diagrammes complexes
- Utilisez **per_slide_config.json** pour varier les rythmes selon la complexité

### Présentations marketing
- Utilisez **entrance_exit_animations.json** pour des effets percutants
- Utilisez **morphing_layers.json** pour des transitions élégantes
- Utilisez **camera_zoom_basic.json** pour mettre en valeur des détails

### Tutoriels et formations
- Utilisez **multi_slide_transitions.json** pour structurer le contenu
- Utilisez **advanced_layer_modes.json** pour corriger/effacer des éléments
- Utilisez **complete_showcase.json** comme référence pour des vidéos professionnelles

### Contenu pour réseaux sociaux
- **Format vertical (9:16)**: Ajoutez `--aspect-ratio 9:16` pour TikTok/Reels
- **Format carré (1:1)**: Ajoutez `--aspect-ratio 1:1` pour Instagram
- **Qualité optimale**: Ajoutez `--quality 18` pour une qualité visually lossless
- **Watermark**: Ajoutez `--watermark logo.png` pour protéger votre contenu

### Récapitulatif des fonctionnalités par fichier

| Fichier | Base | Layers | Animations | Caméra | Transitions | Niveau |
|---------|------|--------|------------|---------|-------------|--------|
| basic_drawing.json | ✅ | ❌ | ❌ | ❌ | ❌ | Débutant |
| multi_slide_transitions.json | ✅ | ❌ | ❌ | ❌ | ✅ | Débutant |
| all_transitions.json | ✅ | ❌ | ❌ | ❌ | ✅ | Débutant |
| per_slide_config.json | ✅ | ❌ | ❌ | ❌ | ✅ | Intermédiaire |
| layers_composition.json | ✅ | ✅ | ❌ | ❌ | ❌ | Intermédiaire |
| advanced_layer_modes.json | ✅ | ✅ | ✅ | ❌ | ❌ | Avancé |
| entrance_exit_animations.json | ✅ | ✅ | ✅ | ❌ | ❌ | Avancé |
| morphing_layers.json | ✅ | ✅ | ✅ | ❌ | ❌ | Avancé |
| camera_zoom_basic.json | ✅ | ❌ | ❌ | ✅ | ❌ | Intermédiaire |
| animation_zoom_in.json | ✅ | ❌ | ✅ | ✅ | ❌ | Avancé |
| camera_and_animation.json | ✅ | ❌ | ✅ | ✅ | ❌ | Avancé |
| multi_layer_camera.json | ✅ | ✅ | ✅ | ✅ | ❌ | Avancé |
| cinematic_reveal.json | ✅ | ❌ | ✅ | ✅ | ❌ | Avancé |
| multi_slide_camera.json | ✅ | ✅ | ✅ | ✅ | ✅ | Expert |
| complete_showcase.json | ✅ | ✅ | ✅ | ✅ | ✅ | Expert |

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
