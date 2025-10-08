# Guide d'utilisation des couches (Layers)

## Vue d'ensemble

La fonctionnalité de couches (layers) permet de superposer plusieurs images sur une même slide, similaire à des applications comme Insta Doodle. Chaque couche peut être positionnée précisément, avoir sa propre vitesse d'animation, et des propriétés visuelles personnalisées.

## Cas d'usage

### 1. Créer une composition complexe

Imaginez que vous voulez créer une animation avec :
- Un fond dégradé
- Un logo en haut à gauche
- Du texte explicatif en bas

Avec les couches, vous pouvez dessiner chaque élément séparément avec son propre timing.

### 2. Animation progressive

Vous pouvez dessiner d'abord le fond lentement, puis ajouter rapidement des éléments graphiques, créant un effet visuel dynamique.

### 3. Compositions multi-éléments

Créez des scènes avec plusieurs éléments superposés, chacun avec sa transparence et son échelle.

## Configuration des couches

### Structure de base

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 4,
      "layers": [
        {
          "image_path": "chemin/vers/image1.png",
          "position": {"x": 0, "y": 0},
          "z_index": 1,
          "skip_rate": 5,
          "scale": 1.0,
          "opacity": 1.0
        }
      ]
    }
  ]
}
```

### Propriétés des couches

#### image_path (requis)
Chemin vers l'image de la couche. Peut être absolu ou relatif au répertoire de travail.

**Exemple :**
```json
"image_path": "assets/background.png"
```

#### position (optionnel, défaut: {x: 0, y: 0})
Position de la couche sur le canvas en pixels.

**Exemple :**
```json
"position": {"x": 100, "y": 50}
```
Place l'image à 100 pixels de la gauche et 50 pixels du haut.

#### z_index (optionnel, défaut: 0)
Ordre de superposition. Plus le nombre est grand, plus la couche est au-dessus.

**Exemple :**
```json
"z_index": 1  // Fond
"z_index": 2  // Éléments intermédiaires
"z_index": 3  // Premier plan
```

Les couches sont dessinées dans l'ordre croissant de z_index.

#### skip_rate (optionnel, hérite de la slide)
Vitesse de dessin de cette couche spécifiquement. Plus le nombre est élevé, plus le dessin est rapide.

**Exemple :**
```json
"skip_rate": 5   // Dessin lent
"skip_rate": 20  // Dessin rapide
```

#### scale (optionnel, défaut: 1.0)
Échelle de l'image. 1.0 = taille originale, 0.5 = 50% de la taille, 2.0 = double taille.

**Exemple :**
```json
"scale": 0.3  // Réduit l'image à 30% de sa taille
```

#### opacity (optionnel, défaut: 1.0)
Opacité de la couche. 1.0 = complètement opaque, 0.0 = invisible.

**Exemple :**
```json
"opacity": 0.8  // 80% d'opacité (légèrement transparent)
```

## Exemples pratiques

### Exemple 1 : Logo + Texte sur fond

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 5,
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
          "skip_rate": 20,
          "scale": 0.3
        },
        {
          "image_path": "title.png",
          "position": {"x": 200, "y": 400},
          "z_index": 3,
          "skip_rate": 25,
          "opacity": 0.9
        }
      ]
    }
  ]
}
```

**Résultat :**
1. Le fond est dessiné lentement (skip_rate: 5)
2. Le logo apparaît ensuite rapidement en haut à gauche, réduit à 30%
3. Le titre apparaît très rapidement en bas, légèrement transparent

### Exemple 2 : Diagramme avec annotations

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 3,
      "layers": [
        {
          "image_path": "diagram.png",
          "position": {"x": 100, "y": 100},
          "z_index": 1,
          "skip_rate": 10
        },
        {
          "image_path": "arrow1.png",
          "position": {"x": 300, "y": 200},
          "z_index": 2,
          "skip_rate": 30
        },
        {
          "image_path": "arrow2.png",
          "position": {"x": 400, "y": 300},
          "z_index": 2,
          "skip_rate": 30
        },
        {
          "image_path": "label1.png",
          "position": {"x": 350, "y": 180},
          "z_index": 3,
          "skip_rate": 40
        }
      ]
    }
  ]
}
```

**Résultat :**
1. Le diagramme principal est dessiné
2. Deux flèches apparaissent rapidement
3. Une étiquette apparaît très rapidement par-dessus

### Exemple 3 : Slides multiples avec et sans couches

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 4,
      "layers": [
        {
          "image_path": "intro_bg.png",
          "position": {"x": 0, "y": 0},
          "z_index": 1,
          "skip_rate": 8
        },
        {
          "image_path": "intro_logo.png",
          "position": {"x": 250, "y": 200},
          "z_index": 2,
          "skip_rate": 20,
          "scale": 0.5
        }
      ]
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
      "duration": 0.8
    }
  ]
}
```

**Utilisation :**
```bash
python whiteboard_animator.py placeholder.png content.png --config config.json
```

**Résultat :**
- Slide 0 : Composition de 2 couches (intro avec logo)
- Transition fade
- Slide 1 : Image unique (content.png) dessinée normalement

## Commandes d'utilisation

### Avec une seule slide contenant des couches

```bash
python whiteboard_animator.py placeholder.png --config layers_config.json
```

**Note :** Vous devez fournir au moins une image en ligne de commande pour définir le nombre de slides, mais cette image sera ignorée pour les slides configurées avec des couches.

### Avec plusieurs slides

```bash
python whiteboard_animator.py slide1.png slide2.png slide3.png --config config.json
```

Les slides avec configuration de couches utiliseront les couches définies, les autres utiliseront l'image fournie en ligne de commande.

### Avec transitions et paramètres additionnels

```bash
python whiteboard_animator.py img1.png img2.png \
  --config layers_config.json \
  --transition fade \
  --frame-rate 30 \
  --export-json
```

## Conseils et astuces

### 1. Organisation des fichiers
Organisez vos images de couches dans un dossier dédié :
```
projet/
├── layers/
│   ├── background.png
│   ├── element1.png
│   └── element2.png
├── config.json
└── placeholder.png
```

### 2. Vitesses de dessin
- **Fond (z_index: 1)** : skip_rate 5-10 (lent, donne du poids)
- **Éléments principaux (z_index: 2)** : skip_rate 10-20 (normal)
- **Détails/annotations (z_index: 3+)** : skip_rate 20-40 (rapide)

### 3. Transparence
Utilisez l'opacité pour créer des effets de superposition subtils :
- Logo d'arrière-plan : opacity 0.3-0.5
- Éléments normaux : opacity 0.8-1.0

### 4. Échelle
Utilisez scale pour éviter de redimensionner les images manuellement :
- Logos : 0.2-0.4
- Icônes : 0.3-0.6
- Images complètes : 0.8-1.0

### 5. Résolution cible
Les positions sont en pixels par rapport à la résolution cible calculée. Utilisez `--get-split-lens` pour connaître la résolution :
```bash
python whiteboard_animator.py image.png --get-split-lens
```

## Dépannage

### Les couches ne s'affichent pas
- Vérifiez que les chemins d'images sont corrects
- Assurez-vous que les positions ne placent pas les couches hors du canvas
- Vérifiez que l'opacité n'est pas à 0

### Les couches sont dans le mauvais ordre
- Vérifiez les valeurs de z_index
- Souvenez-vous : plus petit z_index = dessiné en premier (derrière)

### Les images sont trop grandes/petites
- Utilisez la propriété `scale` pour ajuster
- Vérifiez la résolution cible de votre vidéo

### Performance lente
- Augmentez les valeurs de skip_rate
- Réduisez la résolution des images de couches
- Utilisez --split-len plus grand (ex: 30 au lieu de 15)

## Limitations

1. **Nombre de couches** : Pas de limite technique, mais gardez-le raisonnable (< 10) pour la performance
2. **Formats d'image** : PNG recommandé pour la transparence
3. **Taille des images** : Proportionnelle à la résolution cible pour de meilleurs résultats
4. **Position** : Les coordonnées négatives ou hors canvas seront tronquées

## Support et contributions

Pour des questions ou suggestions concernant les couches, ouvrez une issue sur GitHub.
