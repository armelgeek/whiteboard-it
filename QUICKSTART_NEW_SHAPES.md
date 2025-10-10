# Quick Start: New Geometric Shapes

Get started with curved arrows, braces, and hand-drawn shapes in 5 minutes!

## Installation

No additional installation needed! The new shapes are part of the existing whiteboard-animator system.

## Quick Examples

### 1. Curved Arrow (30 seconds)

Create a smooth curved arrow:

```json
{
  "slides": [{
    "index": 0,
    "duration": 5,
    "layers": [{
      "type": "shape",
      "shape_config": {
        "shape": "curved_arrow",
        "curve_type": "quadratic",
        "points": [[100, 400], [640, 100], [1180, 400]],
        "color": "#FF0000",
        "stroke_width": 4,
        "arrow_size": 35
      },
      "mode": "draw",
      "skip_rate": 10
    }]
  }]
}
```

Save as `my_curved_arrow.json` and run:
```bash
python whiteboard_animator.py --config my_curved_arrow.json
```

### 2. Brace for Grouping (30 seconds)

Add curly braces to group content:

```json
{
  "slides": [{
    "index": 0,
    "duration": 5,
    "layers": [{
      "type": "shape",
      "shape_config": {
        "shape": "brace",
        "orientation": "left",
        "position": {"x": 200, "y": 450},
        "width": 40,
        "height": 300,
        "color": "#000000",
        "stroke_width": 3
      },
      "mode": "draw",
      "skip_rate": 12
    }]
  }]
}
```

### 3. Hand-Drawn Rectangle (30 seconds)

Create a sketchy, hand-drawn style rectangle:

```json
{
  "slides": [{
    "index": 0,
    "duration": 5,
    "layers": [{
      "type": "shape",
      "shape_config": {
        "shape": "sketchy_rectangle",
        "position": {"x": 640, "y": 450},
        "width": 400,
        "height": 250,
        "color": "#0066CC",
        "stroke_width": 2,
        "roughness": 3,
        "iterations": 3
      },
      "mode": "draw",
      "skip_rate": 8
    }]
  }]
}
```

### 4. Hand-Drawn Circle (30 seconds)

Circle important content with a hand-drawn circle:

```json
{
  "slides": [{
    "index": 0,
    "duration": 5,
    "layers": [{
      "type": "shape",
      "shape_config": {
        "shape": "sketchy_circle",
        "position": {"x": 640, "y": 450},
        "size": 150,
        "color": "#FF6600",
        "stroke_width": 2,
        "roughness": 3,
        "iterations": 3
      },
      "mode": "draw",
      "skip_rate": 10
    }]
  }]
}
```

## Shape Parameters Cheat Sheet

### Curved Arrow
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `curve_type` | No | "quadratic" | "quadratic" or "cubic" |
| `points` | Yes | - | 3 points (quadratic) or 4 points (cubic) |
| `arrow_size` | No | 20 | Size of arrow head |
| `num_segments` | No | 50 | Curve smoothness (higher = smoother) |

### Brace
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `orientation` | No | "left" | "left", "right", "top", "bottom" |
| `width` | Yes | - | Width of brace |
| `height` | Yes | - | Height of brace |
| `tip_size` | No | width*0.3 | Size of middle tip |

### Sketchy Rectangle
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `width` | Yes | - | Rectangle width |
| `height` | Yes | - | Rectangle height |
| `roughness` | No | 2 | Amount of variation (1-5 recommended) |
| `iterations` | No | 3 | Number of overlapping strokes (1-5) |

### Sketchy Circle
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `size` | Yes | - | Radius of circle |
| `roughness` | No | 2 | Amount of variation (1-5 recommended) |
| `iterations` | No | 3 | Number of overlapping strokes (1-5) |

## Common Use Cases

### Use Case 1: Flow Diagram with Curved Arrow
```json
// Show flow from one element to another with a smooth curve
{
  "shape": "curved_arrow",
  "curve_type": "quadratic",
  "points": [[200, 300], [640, 100], [1080, 300]],
  "color": "#0066CC"
}
```

### Use Case 2: Mathematical Notation with Braces
```json
// Group related items with left and right braces
{
  "shape": "brace",
  "orientation": "left",
  "position": {"x": 150, "y": 450},
  "width": 30,
  "height": 200
}
```

### Use Case 3: Highlighting with Sketchy Circle
```json
// Circle important text or elements
{
  "shape": "sketchy_circle",
  "position": {"x": 640, "y": 450},
  "size": 120,
  "roughness": 3
}
```

### Use Case 4: Framing Content with Sketchy Rectangle
```json
// Frame a section with a hand-drawn rectangle
{
  "shape": "sketchy_rectangle",
  "position": {"x": 640, "y": 450},
  "width": 500,
  "height": 300,
  "roughness": 4
}
```

## Tips & Tricks

### Curved Arrows
- **Quadratic** (3 points): Use for simple arcs
- **Cubic** (4 points): Use for S-curves
- Increase `num_segments` for smoother curves (default: 50)
- Control points don't need to be on the line

### Braces
- Use **left/right** for vertical grouping
- Use **top/bottom** for horizontal grouping
- Adjust `tip_size` to make the middle tip larger or smaller
- Works great with text layers for mathematical notation

### Sketchy Shapes
- `roughness` controls variation (2-4 works well)
- `iterations` controls how many overlapping strokes (3 is standard)
- Higher values = more hand-drawn effect but slower rendering
- Each render is slightly different due to randomness

### Animation
- All shapes support `mode: "draw"` for progressive drawing
- Use `skip_rate` to control drawing speed (higher = faster)
- Add entrance/exit animations for extra effects
- Combine with static mode for instant display

## Testing Your Shapes

Run the test suite to verify everything works:

```bash
# Test new shapes
python test_new_shapes.py

# Create visual showcase
python create_showcase.py

# Check output
ls -l /tmp/test_*.png
```

## Complete Example

See `example_new_shapes.json` for a full configuration with all new shape types.

## Next Steps

1. ✅ Try the quick examples above
2. ✅ Modify parameters to see effects
3. ✅ Combine multiple shapes in one slide
4. ✅ Add entrance/exit animations
5. ✅ Read [SHAPES_GUIDE.md](SHAPES_GUIDE.md) for detailed docs

## Troubleshooting

**Problem**: Curved arrow looks jagged
- **Solution**: Increase `num_segments` to 80-100

**Problem**: Sketchy shapes look too perfect
- **Solution**: Increase `roughness` to 4-5 and `iterations` to 4-5

**Problem**: Brace too small/large
- **Solution**: Adjust `width` and `height` parameters

**Problem**: Shape not animating
- **Solution**: Make sure `mode: "draw"` is set

## Support

For more information:
- [NEW_SHAPES_README.md](NEW_SHAPES_README.md) - Feature overview
- [SHAPES_GUIDE.md](SHAPES_GUIDE.md) - Complete documentation
- [example_new_shapes.json](example_new_shapes.json) - Working example

Happy animating! 🎨
