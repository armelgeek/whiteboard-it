# Hand Push Animation Feature

## Overview

The hand push animation feature allows you to animate objects being pushed into the scene by a visible hand. This creates a more interactive and engaging effect compared to standard slide-in animations.

## How It Works

When you use a `push_from_*` animation type, the system:
1. Animates the object sliding in from the specified direction
2. Overlays a hand image that appears to be pushing the object
3. Synchronizes the hand position with the object movement
4. Gradually fades or slides the hand along with the object

## Animation Types

The following push animation types are available:

- `push_from_left`: Hand pushes object from the left side
- `push_from_right`: Hand pushes object from the right side
- `push_from_top`: Hand pushes object from the top
- `push_from_bottom`: Hand pushes object from the bottom

## Configuration

Add a push animation to a layer using the `entrance_animation` property:

```json
{
  "image_path": "demo/laptop.png",
  "position": {"x": 100, "y": 100},
  "z_index": 2,
  "scale": 0.4,
  "mode": "static",
  "entrance_animation": {
    "type": "push_from_left",
    "duration": 1.5
  }
}
```

### Parameters

- **type** (string): The push animation type (`push_from_left`, `push_from_right`, `push_from_top`, or `push_from_bottom`)
- **duration** (float): Animation duration in seconds (recommended: 1.0-2.0 seconds)

## Example Configuration

See `examples/push_animation_example.json` for a complete example showing multiple objects being pushed from different directions.

```json
{
  "slides": [
    {
      "index": 0,
      "duration": 12,
      "layers": [
        {
          "image_path": "demo/background.jpg",
          "position": {"x": 0, "y": 0},
          "z_index": 1,
          "skip_rate": 10,
          "mode": "draw"
        },
        {
          "image_path": "demo/laptop.png",
          "position": {"x": 100, "y": 100},
          "z_index": 2,
          "scale": 0.4,
          "mode": "static",
          "entrance_animation": {
            "type": "push_from_left",
            "duration": 1.5
          }
        }
      ]
    }
  ]
}
```

## Usage

Run the animation with your configuration file:

```bash
python whiteboard_animator.py --config examples/push_animation_example.json
```

## Technical Details

### Hand Positioning

The hand is automatically positioned relative to the object being pushed:

- **push_from_left**: Hand appears at the left edge of the object
- **push_from_right**: Hand appears at the right edge of the object
- **push_from_top**: Hand appears at the top edge of the object
- **push_from_bottom**: Hand appears at the bottom edge of the object

The hand offset is calculated as 30% of the hand's width/height to create a natural pushing appearance.

### Performance

Push animations use the same frame-based rendering as other entrance animations, ensuring smooth playback at your configured frame rate (default: 30 FPS).

## Comparison with Other Animations

| Animation Type | Hand Visible | Use Case |
|---------------|--------------|----------|
| `slide_in_*` | No | Simple, clean transitions |
| `push_from_*` | Yes | Interactive, engaging presentations |
| `fade_in` | No | Subtle appearances |
| `zoom_in` | No | Dramatic reveals |

## Tips

1. **Duration**: Use 1.0-2.0 seconds for push animations - shorter feels rushed, longer feels slow
2. **Layer Mode**: Use `"mode": "static"` for objects with push animations (no drawing animation needed)
3. **Z-Index**: Ensure proper layering - the hand will appear on top of the pushed object
4. **Scale**: Adjust object scale to match your scene composition
5. **Multiple Objects**: Stagger push animations by adjusting layer order and duration

## Compatibility

- Compatible with all existing layer modes (`draw`, `static`, `eraser`)
- Works with opacity settings
- Can be combined with `exit_animation` for complete control
- Supports all output formats and aspect ratios

## Related Features

- **Entrance Animations**: See `IMPLEMENTATION_ANIMATIONS.md` for other entrance animation types
- **Exit Animations**: Configure object exits with `exit_animation`
- **Layer System**: See `LAYERS_GUIDE.md` for comprehensive layer documentation
