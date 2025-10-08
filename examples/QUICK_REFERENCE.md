# Guide de référence rapide - Exemples

Ce guide vous aide à choisir le bon exemple selon vos besoins.

## Par niveau de difficulté

### 🟢 Débutant (Commencez ici!)

1. **basic_drawing.json** - Animation simple
   ```bash
   python whiteboard_animator.py demo/1.jpg --config examples/basic_drawing.json --split-len 30
   ```

2. **multi_slide_transitions.json** - Plusieurs images avec transitions
   ```bash
   python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png --config examples/multi_slide_transitions.json --split-len 30
   ```

3. **all_transitions.json** - Tous les types de transitions
   ```bash
   python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png demo/1.jpg demo/2.jpg demo/3.png --config examples/all_transitions.json --split-len 30
   ```

### 🟡 Intermédiaire

4. **layers_composition.json** - Superposition d'images
   ```bash
   python whiteboard_animator.py demo/placeholder.png --config examples/layers_composition.json --split-len 30
   ```

5. **per_slide_config.json** - Configuration avancée par slide
   ```bash
   python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png --config examples/per_slide_config.json --split-len 30
   ```

6. **camera_zoom_basic.json** - Zoom de caméra basique
   ```bash
   python whiteboard_animator.py demo/1.jpg --config examples/camera_zoom_basic.json --split-len 30
   ```

### 🔴 Avancé

7. **advanced_layer_modes.json** - Modes draw/eraser/static
   ```bash
   python whiteboard_animator.py demo/placeholder.png --config examples/advanced_layer_modes.json --split-len 30
   ```

8. **entrance_exit_animations.json** - Animations d'apparition/disparition
   ```bash
   python whiteboard_animator.py demo/placeholder.png --config examples/entrance_exit_animations.json --split-len 30
   ```

9. **morphing_layers.json** - Morphing entre couches
   ```bash
   python whiteboard_animator.py demo/placeholder.png --config examples/morphing_layers.json --split-len 30
   ```

10. **animation_zoom_in.json** - Animation post-dessin
    ```bash
    python whiteboard_animator.py demo/1.jpg --config examples/animation_zoom_in.json --split-len 30
    ```

11. **cinematic_reveal.json** - Effet cinématique
    ```bash
    python whiteboard_animator.py demo/1.jpg --config examples/cinematic_reveal.json --split-len 30
    ```

### ⭐ Expert

12. **complete_showcase.json** - Tous les concepts combinés
    ```bash
    python whiteboard_animator.py demo/placeholder.png demo/placeholder.png --config examples/complete_showcase.json --split-len 30
    ```

## Par fonctionnalité recherchée

### Transitions entre slides
- **all_transitions.json** - Voir tous les effets de transition
- **multi_slide_transitions.json** - Transitions fade et iris
- **per_slide_config.json** - Transitions avec pauses

### Couches multiples (Layers)
- **layers_composition.json** - Superposition simple
- **advanced_layer_modes.json** - Modes draw/eraser/static
- **entrance_exit_animations.json** - Apparitions/disparitions
- **morphing_layers.json** - Transitions fluides

### Contrôles de caméra
- **camera_zoom_basic.json** - Zoom statique
- **animation_zoom_in.json** - Zoom progressif post-dessin
- **camera_and_animation.json** - Combinaison de zooms
- **cinematic_reveal.json** - Effet dramatique

### Configuration avancée
- **per_slide_config.json** - Durées et vitesses personnalisées
- **complete_showcase.json** - Configuration complexe

## Options de ligne de commande

### Qualité et formats (ne nécessitent pas de fichier JSON)

```bash
# Format vertical pour TikTok/Reels (9:16)
python whiteboard_animator.py demo/1.jpg --aspect-ratio 9:16 --quality 18

# Format carré pour Instagram (1:1)
python whiteboard_animator.py demo/1.jpg --aspect-ratio 1:1 --quality 18

# Format paysage HD pour YouTube (16:9)
python whiteboard_animator.py demo/1.jpg --aspect-ratio 16:9 --quality 18

# Qualité maximale (visually lossless)
python whiteboard_animator.py demo/1.jpg --quality 18

# Qualité moyenne (fichiers plus légers)
python whiteboard_animator.py demo/1.jpg --quality 28
```

### Watermark (filigrane)

```bash
# Ajouter un logo en bas à droite
python whiteboard_animator.py demo/1.jpg --watermark logo.png

# Logo personnalisé (position, opacité, taille)
python whiteboard_animator.py demo/1.jpg \
  --watermark logo.png \
  --watermark-position top-right \
  --watermark-opacity 0.7 \
  --watermark-scale 0.15
```

### Export JSON

```bash
# Exporter les données d'animation
python whiteboard_animator.py demo/1.jpg --export-json

# Avec configuration et export
python whiteboard_animator.py demo/1.jpg \
  --config examples/basic_drawing.json \
  --export-json
```

### Combinaisons populaires

```bash
# Présentation verticale avec logo (TikTok/Reels)
python whiteboard_animator.py demo/1.jpg demo/2.jpg \
  --config examples/multi_slide_transitions.json \
  --aspect-ratio 9:16 \
  --quality 18 \
  --watermark logo.png \
  --watermark-position bottom-right

# Vidéo YouTube HD avec transitions
python whiteboard_animator.py demo/1.jpg demo/2.jpg demo/3.png \
  --config examples/all_transitions.json \
  --aspect-ratio 16:9 \
  --quality 18

# Post Instagram carré avec couches
python whiteboard_animator.py demo/placeholder.png \
  --config examples/layers_composition.json \
  --aspect-ratio 1:1 \
  --quality 18
```

## Créer vos propres configurations

Copiez un exemple existant et modifiez-le:

```bash
# Copier un exemple
cp examples/basic_drawing.json my_config.json

# Éditer avec votre éditeur préféré
nano my_config.json

# Utiliser votre configuration
python whiteboard_animator.py demo/1.jpg --config my_config.json --split-len 30
```

## Astuces

- **Vitesse de dessin** : Plus le `skip_rate` est élevé, plus le dessin est rapide
- **Durée** : Le paramètre `duration` est la durée TOTALE (animation + affichage final)
- **Résolution** : Utilisez `--split-len 30` ou plus pour un traitement rapide
- **Qualité** : `--quality 18` = qualité maximale, `--quality 28` = compromis taille/qualité

## Documentation complète

- **[examples/README.md](README.md)** - Documentation détaillée de tous les exemples
- **[CONFIG_FORMAT.md](../CONFIG_FORMAT.md)** - Format de configuration JSON complet
- **[LAYERS_GUIDE.md](../LAYERS_GUIDE.md)** - Guide complet des couches
- **[CAMERA_ANIMATION_GUIDE.md](../CAMERA_ANIMATION_GUIDE.md)** - Contrôles de caméra
- **[README.md](../README.md)** - Documentation générale du projet
