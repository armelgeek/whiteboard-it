# Transitions entre Slides

Ce document décrit les fonctionnalités de transition implémentées pour les animations de type "whiteboard".

## Fonctionnalités

### 1. Transitions
Lorsque plusieurs images sont combinées en une seule vidéo, des transitions peuvent être appliquées entre chaque slide.

#### Types de transitions disponibles:

- **none** : Pas de transition (changement instantané)
- **fade** : Fondu enchaîné entre les slides
- **wipe** : Balayage de gauche à droite
- **push_left** : Pousse la slide actuelle vers la gauche
- **push_right** : Pousse la slide actuelle vers la droite
- **iris** : Transition en cercle qui s'agrandit depuis le centre

### 2. Vitesse de dessin (Drawing Speed)
Contrôlé par le paramètre `--skip-rate`.

- Plus la valeur est élevée, plus le dessin est rapide
- Par défaut: 8
- Exemple: `--skip-rate 20` dessine plus rapidement

### 3. Durée de la slide (Slide Duration)
Contrôlé par le paramètre `--duration`.

- Définit combien de secondes l'image finale reste affichée
- Par défaut: 3 secondes
- Exemple: `--duration 5` affiche l'image finale pendant 5 secondes

### 4. Durée de transition (Transition Duration)
Contrôlé par le paramètre `--transition-duration`.

- Définit la durée de la transition entre les slides
- Par défaut: 0.5 secondes
- Exemple: `--transition-duration 1.0` crée une transition d'une seconde

## Exemples d'utilisation

### Transition simple
```bash
python whiteboard_animator.py slide1.png slide2.png --transition fade
```

### Transition personnalisée
```bash
python whiteboard_animator.py img1.png img2.png img3.png \
  --transition iris \
  --transition-duration 1.0
```

### Configuration complète
```bash
python whiteboard_animator.py slide1.png slide2.png slide3.png \
  --transition fade \
  --transition-duration 0.8 \
  --skip-rate 15 \
  --duration 3 \
  --frame-rate 30 \
  --export-json
```

## Détails techniques

### Implémentation des transitions

Les transitions sont implémentées dans la fonction `generate_transition_frames()` qui génère des frames intermédiaires entre deux slides:

1. **Fade**: Utilise `cv2.addWeighted()` pour créer un fondu progressif
2. **Wipe**: Remplace progressivement les colonnes de pixels de gauche à droite
3. **Push Left/Right**: Déplace les pixels avec un offset progressif
4. **Iris**: Utilise un masque circulaire qui s'agrandit progressivement

### Nombre de frames de transition

Le nombre de frames générées est calculé par:
```
num_frames = fps × transition_duration
```

Exemple: À 30 FPS avec une durée de 0.5s, 15 frames de transition sont générées.

## Prérequis

Les transitions nécessitent:
- `opencv-python` (cv2)
- `numpy`
- `av` (PyAV) pour la concaténation vidéo

Installation:
```bash
pip install opencv-python numpy av
```

## Notes

- Les transitions ne sont appliquées qu'entre les vidéos lors de la concaténation
- Si une seule image est fournie, aucune transition n'est appliquée
- La transition `none` est utile si vous voulez désactiver les transitions tout en combinant plusieurs images
