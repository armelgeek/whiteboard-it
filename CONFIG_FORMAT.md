# Configuration personnalisée par slide

Ce document décrit le format du fichier de configuration JSON pour personnaliser les paramètres de chaque slide individuellement.

## Format du fichier JSON

Le fichier de configuration contient deux sections principales :
- `slides` : Configuration spécifique à chaque slide
- `transitions` : Configuration des transitions entre les slides

### Exemple complet

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
    },
    {
      "index": 2,
      "duration": 4,
      "skip_rate": 8
    }
  ],
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 0.8,
      "pause_before": 1.0
    },
    {
      "after_slide": 1,
      "type": "wipe",
      "duration": 1.0,
      "pause_before": 0.5
    }
  ]
}
```

## Section `slides`

Permet de définir des paramètres spécifiques pour chaque slide.

### Propriétés disponibles

| Propriété | Type | Description | Par défaut |
|-----------|------|-------------|------------|
| `index` | int | Index de la slide (commence à 0) | Requis |
| `duration` | int/float | Durée d'affichage de la slide finale en secondes | Valeur globale `--duration` |
| `skip_rate` | int | Vitesse de dessin (plus grand = plus rapide) | Valeur globale `--skip-rate` |

### Exemple

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 2,
      "skip_rate": 10
    }
  ]
}
```

Dans cet exemple :
- La première slide (index 0) sera affichée pendant 2 secondes après le dessin
- Le dessin sera effectué avec une vitesse de 10 (plus rapide que la valeur par défaut de 8)

## Section `transitions`

Permet de définir des transitions personnalisées entre les slides.

### Propriétés disponibles

| Propriété | Type | Description | Par défaut |
|-----------|------|-------------|------------|
| `after_slide` | int | Index de la slide après laquelle appliquer la transition (commence à 0) | Requis |
| `type` | string | Type de transition : `none`, `fade`, `wipe`, `push_left`, `push_right`, `iris` | Valeur globale `--transition` |
| `duration` | float | Durée de la transition en secondes | Valeur globale `--transition-duration` |
| `pause_before` | float | Durée de pause avant la transition (en secondes) | 0 |

### Exemple

```json
{
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

Dans cet exemple :
- Après la première slide (index 0), il y aura une pause de 1 seconde
- Puis une transition de type "fade" d'une durée de 0.8 secondes vers la slide suivante

## Types de transitions disponibles

- **`none`** : Pas de transition (changement instantané)
- **`fade`** : Fondu enchaîné entre les slides
- **`wipe`** : Balayage de gauche à droite
- **`push_left`** : Pousse la slide actuelle vers la gauche
- **`push_right`** : Pousse la slide actuelle vers la droite
- **`iris`** : Transition en cercle qui s'agrandit depuis le centre

## Utilisation

### Créer un fichier de configuration

1. Créez un fichier JSON (par exemple `my_config.json`)
2. Définissez vos paramètres personnalisés
3. Utilisez le paramètre `--config` pour l'appliquer

```bash
python whiteboard_animator.py slide1.png slide2.png slide3.png --config my_config.json
```

### Exemple d'utilisation avancée

```bash
# Configuration complète avec paramètres globaux et personnalisés
python whiteboard_animator.py slide1.png slide2.png slide3.png \
  --config my_config.json \
  --frame-rate 30 \
  --split-len 15 \
  --export-json
```

Dans cet exemple :
- Le fichier `my_config.json` définit les paramètres personnalisés par slide
- Les paramètres globaux (`--frame-rate`, `--split-len`) s'appliquent à toutes les slides sauf si surchargés dans le fichier de configuration
- Les données d'animation sont exportées au format JSON

## Comportement par défaut

Si une propriété n'est pas spécifiée dans le fichier de configuration :
- Les valeurs des paramètres CLI globaux seront utilisées
- Si aucun paramètre CLI n'est spécifié, les valeurs par défaut du programme seront utilisées

## Exemples de cas d'usage

### Cas 1 : Vitesses de dessin différentes

```json
{
  "slides": [
    {
      "index": 0,
      "skip_rate": 5
    },
    {
      "index": 1,
      "skip_rate": 20
    },
    {
      "index": 2,
      "skip_rate": 10
    }
  ]
}
```

La première slide sera dessinée lentement (5), la deuxième rapidement (20), et la troisième à vitesse moyenne (10).

### Cas 2 : Durées d'affichage personnalisées

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 1
    },
    {
      "index": 1,
      "duration": 5
    },
    {
      "index": 2,
      "duration": 2
    }
  ]
}
```

La première slide s'affiche 1 seconde, la deuxième 5 secondes, et la troisième 2 secondes après leur dessin.

### Cas 3 : Transitions variées avec pauses

```json
{
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 0.5,
      "pause_before": 2.0
    },
    {
      "after_slide": 1,
      "type": "iris",
      "duration": 1.5,
      "pause_before": 1.0
    }
  ]
}
```

- Après la slide 1 : pause de 2 secondes, puis transition fade de 0.5 seconde
- Après la slide 2 : pause de 1 seconde, puis transition iris de 1.5 secondes

### Cas 4 : Configuration complète

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
      "duration": 3,
      "skip_rate": 15
    },
    {
      "index": 2,
      "duration": 4,
      "skip_rate": 10
    }
  ],
  "transitions": [
    {
      "after_slide": 0,
      "type": "fade",
      "duration": 0.8,
      "pause_before": 1.5
    },
    {
      "after_slide": 1,
      "type": "wipe",
      "duration": 1.0,
      "pause_before": 2.0
    }
  ]
}
```

Cet exemple combine tous les paramètres :
- Chaque slide a sa propre durée d'affichage et vitesse de dessin
- Chaque transition a son propre type, durée et temps de pause

## Notes importantes

1. **Index des slides** : Les index commencent à 0 (première slide = index 0)
2. **Index des transitions** : `after_slide` indique l'index de la slide AVANT la transition
3. **Compatibilité** : Si vous spécifiez des paramètres globaux via CLI ET un fichier de configuration, les valeurs du fichier de configuration ont la priorité pour les slides spécifiées
4. **Slides non configurées** : Les slides non mentionnées dans le fichier de configuration utiliseront les paramètres globaux
5. **Validation** : Le programme ne valide pas strictement la structure JSON, assurez-vous que votre fichier est bien formaté

## Dépannage

### Erreur "Fichier de configuration introuvable"
Vérifiez que le chemin vers votre fichier JSON est correct et que le fichier existe.

### Les paramètres ne sont pas appliqués
Assurez-vous que :
- Le format JSON est valide (utilisez un validateur JSON en ligne)
- Les index correspondent bien à vos slides (commence à 0)
- Les types de transition sont bien orthographiés

### Transitions incorrectes
Vérifiez que `after_slide` pointe vers le bon index (0 pour après la première slide, 1 pour après la deuxième, etc.)
