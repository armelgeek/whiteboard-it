# Whiteboard-It

Application de création d'animations de type "dessin sur tableau blanc" (whiteboard animation) à partir d'images.

## Fonctionnalités

- ✅ Génération de vidéos d'animation de dessin à partir d'images
- ✅ **Couches multiples (layers)** - Superposition d'images sur une même slide avec hiérarchie (NOUVEAU)
- ✅ **Qualité vidéo améliorée** - CRF ajustable pour une qualité optimale
- ✅ **Export multi-formats** - Support 1:1, 16:9, 9:16 en HD
- ✅ **Filigrane (watermark)** - Ajout de logo/texte avec position et opacité personnalisables
- ✅ **Support de plusieurs images avec combinaison automatique**
- ✅ **Transitions entre slides** (fade, wipe, push, iris)
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

### Qualité vidéo et formats d'export (NOUVEAU)

```bash
# Haute qualité pour YouTube (16:9 HD)
python whiteboard_animator.py image.png --aspect-ratio 16:9 --quality 18

# Format vertical pour TikTok/Reels (9:16 HD)
python whiteboard_animator.py image.png --aspect-ratio 9:16 --quality 18

# Format carré pour Instagram (1:1)
python whiteboard_animator.py image.png --aspect-ratio 1:1 --quality 18

# Qualité moyenne pour fichiers plus légers
python whiteboard_animator.py image.png --quality 28
```

### Ajouter un filigrane (watermark) (NOUVEAU)

```bash
# Ajouter un filigrane en bas à droite
python whiteboard_animator.py image.png --watermark logo.png

# Filigrane personnalisé (position, opacité, taille)
python whiteboard_animator.py image.png \
  --watermark logo.png \
  --watermark-position top-right \
  --watermark-opacity 0.7 \
  --watermark-scale 0.15

# Combinaison: Qualité HD 16:9 avec filigrane
python whiteboard_animator.py image.png \
  --aspect-ratio 16:9 \
  --quality 18 \
  --watermark logo.png \
  --watermark-position bottom-right \
  --watermark-opacity 0.5
```

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

### Paramètres de base
- `--split-len` : Taille de la grille pour le dessin (par défaut: 15)
- `--frame-rate` : Images par seconde (par défaut: 30)
- `--skip-rate` : Vitesse de dessin (plus grand = plus rapide, par défaut: 8)
- `--duration` : Durée de l'image finale en secondes (par défaut: 3)

### Paramètres de qualité et format (NOUVEAU)
- `--quality` : Qualité vidéo CRF (0-51, plus bas = meilleure qualité, par défaut: 18)
  - 18 = Visually lossless (qualité maximale recommandée)
  - 23 = Haute qualité (bon compromis)
  - 28 = Qualité moyenne (fichiers plus petits)
- `--aspect-ratio` : Ratio d'aspect de la vidéo (par défaut: original)
  - `original` : Conserve le ratio d'aspect de l'image source
  - `1:1` : Format carré (Instagram, profils)
  - `16:9` : Format paysage HD (YouTube, télévision)
  - `9:16` : Format vertical (Stories, Reels, TikTok)

### Paramètres de filigrane (NOUVEAU)
- `--watermark` : Chemin vers l'image de filigrane (watermark) à appliquer
- `--watermark-position` : Position du filigrane (par défaut: bottom-right)
  - Choix: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center`
- `--watermark-opacity` : Opacité du filigrane (0.0 à 1.0, par défaut: 0.5)
- `--watermark-scale` : Échelle du filigrane par rapport à la largeur de la vidéo (0.0 à 1.0, par défaut: 0.1)

### Paramètres de transition
- `--transition` : Type de transition entre les slides - choix: none, fade, wipe, push_left, push_right, iris (par défaut: none)
- `--transition-duration` : Durée de la transition en secondes (par défaut: 0.5)

### Autres paramètres
- `--config` : Fichier JSON pour une configuration personnalisée par slide (durée, vitesse, transitions, pauses, etc.)
- `--export-json` : Exporter les données d'animation au format JSON
- `--get-split-lens` : Afficher les valeurs recommandées pour split-len

## Configuration personnalisée par slide

Utilisez le paramètre `--config` avec un fichier JSON pour personnaliser chaque slide individuellement :

```bash
python whiteboard_animator.py slide1.png slide2.png slide3.png --config config.json
```

Le fichier de configuration permet de définir :
- **Durée d'affichage** différente pour chaque slide
- **Vitesse de dessin** (skip-rate) différente pour chaque slide
- **Type de transition** spécifique entre chaque slide
- **Durée de transition** personnalisée entre chaque slide
- **Pause avant transition** pour ajouter un temps d'attente entre les slides

### Exemple de fichier de configuration

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 2,
      "skip_rate": 10
    },
    {
      "index": 1,
      "duration": 3,
      "skip_rate": 15
    }
  ],
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 0.8,
      "pause_before": 1.0
    }
  ]
}
```

Voir [CONFIG_FORMAT.md](CONFIG_FORMAT.md) pour la documentation complète du format de configuration.

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

# Avec configuration personnalisée par slide
python whiteboard_animator.py slide1.png slide2.png slide3.png --config my_config.json

# Configuration personnalisée + paramètres globaux
python whiteboard_animator.py slide1.png slide2.png slide3.png \
  --config my_config.json \
  --frame-rate 30 \
  --export-json
```

### Configuration personnalisée avancée

Créez un fichier `advanced_config.json` :

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 2,
      "skip_rate": 8
    },
    {
      "index": 1,
      "duration": 4,
      "skip_rate": 20
    },
    {
      "index": 2,
      "duration": 3,
      "skip_rate": 12
    }
  ],
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 1.0,
      "pause_before": 2.0
    },
    {
      "after_slide": 1,
      "type": "iris",
      "duration": 1.5,
      "pause_before": 1.5
    }
  ]
}
```

Puis utilisez-le :

```bash
python whiteboard_animator.py slide1.png slide2.png slide3.png --config advanced_config.json
```

Ce fichier de configuration :
- Définit des durées et vitesses différentes pour chaque slide
- Ajoute une pause de 2 secondes après la première slide avant la transition fade
- Ajoute une pause de 1.5 secondes après la deuxième slide avant la transition iris

### Utilisation des couches multiples (layers) (NOUVEAU)

Les couches permettent de superposer plusieurs images sur une même slide, chacune avec sa position, son ordre de superposition (z-index) et sa vitesse de dessin.

Créez un fichier `layers_config.json` :

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 4,
      "layers": [
        {
          "image_path": "background.png",
          "position": {"x": 0, "y": 0},
          "z_index": 1,
          "skip_rate": 5
        },
        {
          "image_path": "logo.png",
          "position": {"x": 50, "y": 50},
          "z_index": 2,
          "skip_rate": 15,
          "scale": 0.3,
          "opacity": 0.9
        },
        {
          "image_path": "text.png",
          "position": {"x": 200, "y": 400},
          "z_index": 3,
          "skip_rate": 20,
          "opacity": 0.8
        }
      ]
    },
    {
      "index": 1,
      "duration": 3,
      "skip_rate": 10
    }
  ],
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 0.5
    }
  ]
}
```

Puis utilisez-le (vous devez toujours fournir au moins une image en ligne de commande) :

```bash
# L'image placeholder.png définit le nombre de slides mais sera ignorée pour la slide 0
python whiteboard_animator.py placeholder.png slide2.png --config layers_config.json
```

**Fonctionnalités des couches :**
- **position** : Positionnement précis (x, y en pixels)
- **z_index** : Ordre de superposition (plus grand = au-dessus)
- **scale** : Échelle de l'image (0.5 = 50%, 1.0 = taille originale)
- **opacity** : Transparence (0.0 = invisible, 1.0 = opaque)
- **skip_rate** : Vitesse de dessin individuelle pour chaque couche

Les couches sont dessinées séquentiellement selon leur z_index, permettant de créer des animations complexes avec plusieurs éléments apparaissant l'un après l'autre sur la même scène.

**Cas d'usage :**
- **Compositions complexes** : Logo + texte + éléments graphiques sur un même fond
- **Animations par étapes** : Dessiner d'abord le fond, puis ajouter des éléments progressivement
- **Créations style "Insta Doodle"** : Superposition d'images avec positions et timing personnalisés


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
