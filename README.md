# Whiteboard-It

Application de création d'animations de type "dessin sur tableau blanc" (whiteboard animation) à partir d'images.

## Fonctionnalités

- ✅ Génération de vidéos d'animation de dessin à partir d'images
- ✅ **Support de plusieurs images avec combinaison automatique** (NOUVEAU)
- ✅ **Transitions entre slides** (fade, wipe, push, iris) (NOUVEAU)
- ✅ Personnalisation des paramètres (FPS, vitesse, grille)
- ✅ Export JSON des données d'animation
- ✅ Support de plusieurs formats d'image
- ✅ Animation avec main réaliste

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/armelgeek/whiteboard-it.git
cd whiteboard-it

# Installer les dépendances de base
pip install opencv-python numpy

# Requis pour la conversion H.264 et la concaténation de vidéos multiples
pip install av
```

**Note:** Le module `av` (PyAV) est fortement recommandé pour :
- La conversion des vidéos en format H.264
- La combinaison de plusieurs images en une seule vidéo

## Utilisation

### Génération de vidéo

```bash
# Génération simple (une image)
python whiteboard_animator.py image.png

# Avec paramètres personnalisés
python whiteboard_animator.py image.png --split-len 15 --frame-rate 30 --skip-rate 8

# Plusieurs images (génère une vidéo combinée)
python whiteboard_animator.py image1.png image2.png image3.png

# Plusieurs images avec paramètres personnalisés
python whiteboard_animator.py image1.png image2.png image3.png --split-len 15 --frame-rate 30 --skip-rate 8
```

**Note:** Lorsque plusieurs images sont fournies, le script génère une vidéo pour chaque image puis les combine automatiquement en une seule vidéo finale. Chaque image est dessinée dans l'ordre.

### Export des données d'animation (JSON)

```bash
# Générer vidéo + données JSON (une image)
python whiteboard_animator.py image.png --export-json

# Plusieurs images avec export JSON (génère un fichier JSON par image)
python whiteboard_animator.py image1.png image2.png image3.png --export-json
```

Cela génère :
- Une vidéo MP4 de l'animation (combinée si plusieurs images)
- Un fichier JSON par image contenant les données d'animation (séquence de dessin, positions de la main, etc.)

### Vérifier les valeurs recommandées

```bash
python whiteboard_animator.py image.png --get-split-lens
```

## Paramètres

- `--split-len` : Taille de la grille pour le dessin (par défaut: 15)
- `--frame-rate` : Images par seconde (par défaut: 30)
- `--skip-rate` : Vitesse de dessin (plus grand = plus rapide, par défaut: 8)
- `--duration` : Durée de l'image finale en secondes (par défaut: 3)
- `--transition` : Type de transition entre les slides - choix: none, fade, wipe, push_left, push_right, iris (par défaut: none)
- `--transition-duration` : Durée de la transition en secondes (par défaut: 0.5)
- `--export-json` : Exporter les données d'animation au format JSON
- `--get-split-lens` : Afficher les valeurs recommandées pour split-len

## Format d'export JSON

Voir [EXPORT_FORMAT.md](EXPORT_FORMAT.md) pour la documentation complète du format JSON.

Les données exportées incluent :
- Métadonnées (résolution, FPS, paramètres)
- Séquence de dessin frame par frame
- Positions de la main pour chaque frame
- Coordonnées des tuiles dessinées

## Exemples d'utilisation

Le dossier [examples/](examples/) contient des scripts d'exemple pour utiliser les données JSON exportées :

```bash
# Analyser une animation
python examples/use_animation_data.py animation.json

# Analyser et exporter une séquence simplifiée
python examples/use_animation_data.py animation.json --export-sequence sequence.json
```

## Cas d'utilisation du format JSON

L'export JSON permet de :
1. **Recréer l'animation** dans d'autres logiciels (After Effects, Blender, VideoScribe, etc.)
2. **Analyser la séquence** pour optimiser les paramètres
3. **Créer des animations personnalisées** en modifiant les données
4. **Intégrer dans des applications web** avec Canvas ou WebGL
5. **Générer des animations procédurales** basées sur les données

## Exemples d'utilisation avancés

### Traitement par lot avec plusieurs images

```bash
# Créer une animation combinée à partir de 3 images
python whiteboard_animator.py slide1.png slide2.png slide3.png

# Avec export JSON pour chaque image
python whiteboard_animator.py slide1.png slide2.png slide3.png --export-json

# Personnaliser la vitesse de dessin
python whiteboard_animator.py img1.png img2.png --skip-rate 15 --duration 2

# Avec transition en fondu entre les slides
python whiteboard_animator.py slide1.png slide2.png slide3.png --transition fade

# Avec transition de type "push left" et durée personnalisée
python whiteboard_animator.py slide1.png slide2.png --transition push_left --transition-duration 1.0

# Tous les types de transitions disponibles
python whiteboard_animator.py img1.png img2.png img3.png --transition iris --transition-duration 0.8
```

### Transitions disponibles

- **none** : Pas de transition (changement instantané)
- **fade** : Fondu enchaîné entre les slides
- **wipe** : Balayage de gauche à droite
- **push_left** : Pousse la slide actuelle vers la gauche
- **push_right** : Pousse la slide actuelle vers la droite
- **iris** : Transition en cercle qui s'agrandit depuis le centre

### Cas d'usage typiques

- **Présentation animée** : Combiner plusieurs diapositives en une vidéo continue
- **Tutoriel illustré** : Dessiner étape par étape des diagrammes ou schémas
- **Story-board animé** : Transformer une série d'images en animation fluide
- **Contenu éducatif** : Créer des vidéos explicatives avec dessins successifs

## Structure du projet

```
whiteboard-it/
├── whiteboard_animator.py   # Script principal
├── data/
│   └── images/              # Images de la main
├── save_videos/             # Dossier de sortie (ignoré par git)
├── examples/                # Scripts d'exemple
│   ├── use_animation_data.py
│   └── README.md
├── EXPORT_FORMAT.md         # Documentation du format JSON
└── README.md               # Ce fichier
```

## Licence

MIT

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou un pull request.
