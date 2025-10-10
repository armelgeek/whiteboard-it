#!/usr/bin/env python3
"""Create a visual showcase of all new shape types."""

import cv2
import numpy as np
from whiteboard_animator import render_shape_to_image

def create_showcase():
    """Create a visual showcase with all new shapes."""
    # Create large canvas
    canvas_width = 1600
    canvas_height = 1200
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    
    # Title text (simulated - just placing shapes)
    print("Creating showcase canvas...")
    
    # Row 1: Curved Arrows
    print("Adding curved arrows...")
    
    # Quadratic curved arrow (downward arc)
    arrow1 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (0, 0, 255),  # Red
        "fill_color": (100, 100, 255),
        "stroke_width": 4,
        "curve_type": "quadratic",
        "points": [[150, 200], [400, 100], [650, 200]],
        "arrow_size": 35
    }, canvas_width, canvas_height)
    
    # Cubic curved arrow (S-curve)
    arrow2 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (255, 0, 0),  # Blue
        "fill_color": (255, 150, 150),
        "stroke_width": 4,
        "curve_type": "cubic",
        "points": [[900, 150], [1000, 100], [1100, 250], [1450, 200]],
        "arrow_size": 35
    }, canvas_width, canvas_height)
    
    # Row 2: Braces
    print("Adding braces...")
    
    # Left brace
    brace1 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 0, 0),
        "stroke_width": 3,
        "orientation": "left",
        "position": {"x": 200, "y": 500},
        "width": 40,
        "height": 250
    }, canvas_width, canvas_height)
    
    # Right brace
    brace2 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 0, 0),
        "stroke_width": 3,
        "orientation": "right",
        "position": {"x": 600, "y": 500},
        "width": 40,
        "height": 250
    }, canvas_width, canvas_height)
    
    # Top brace
    brace3 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 128, 0),  # Green
        "stroke_width": 3,
        "orientation": "top",
        "position": {"x": 1200, "y": 400},
        "width": 250,
        "height": 40
    }, canvas_width, canvas_height)
    
    # Bottom brace
    brace4 = render_shape_to_image({
        "shape": "brace",
        "color": (128, 0, 128),  # Purple
        "stroke_width": 3,
        "orientation": "bottom",
        "position": {"x": 1200, "y": 600},
        "width": 250,
        "height": 40
    }, canvas_width, canvas_height)
    
    # Row 3: Sketchy Shapes
    print("Adding sketchy shapes...")
    
    # Sketchy rectangle 1
    sketchy1 = render_shape_to_image({
        "shape": "sketchy_rectangle",
        "color": (0, 0, 0),
        "stroke_width": 2,
        "position": {"x": 300, "y": 900},
        "width": 350,
        "height": 200,
        "roughness": 3,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Sketchy circle 1
    sketchy2 = render_shape_to_image({
        "shape": "sketchy_circle",
        "color": (0, 0, 255),  # Red
        "stroke_width": 2,
        "position": {"x": 900, "y": 900},
        "size": 150,
        "roughness": 3,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Sketchy circle 2 (smaller, overlapping for effect)
    sketchy3 = render_shape_to_image({
        "shape": "sketchy_circle",
        "color": (255, 0, 0),  # Blue
        "stroke_width": 2,
        "position": {"x": 1200, "y": 900},
        "size": 120,
        "roughness": 4,
        "iterations": 4
    }, canvas_width, canvas_height)
    
    # Combine all shapes onto canvas
    print("Combining shapes...")
    for shape in [arrow1, arrow2, brace1, brace2, brace3, brace4, sketchy1, sketchy2, sketchy3]:
        if shape is not None:
            # Take non-white pixels from shape and overlay
            mask = np.all(shape < 250, axis=2)
            canvas[mask] = shape[mask]
    
    # Add some labels using OpenCV text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "Curved Arrows", (250, 50), font, 1, (0, 0, 0), 2)
    cv2.putText(canvas, "Quadratic", (250, 280), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Cubic (S-curve)", (950, 280), font, 0.6, (100, 100, 100), 1)
    
    cv2.putText(canvas, "Braces (Accolades)", (550, 350), font, 1, (0, 0, 0), 2)
    cv2.putText(canvas, "Left", (130, 650), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Right", (620, 650), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Top", (1150, 370), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Bottom", (1120, 650), font, 0.6, (100, 100, 100), 1)
    
    cv2.putText(canvas, "Hand-Drawn/Sketchy Shapes", (500, 750), font, 1, (0, 0, 0), 2)
    cv2.putText(canvas, "Sketchy Rectangle", (170, 1050), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Sketchy Circle", (800, 1050), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Sketchy Circle (more rough)", (1050, 1050), font, 0.6, (100, 100, 100), 1)
    
    # Save the showcase
    output_path = "/tmp/new_shapes_showcase.png"
    cv2.imwrite(output_path, canvas)
    print(f"\n✓ Showcase saved to {output_path}")
    
    return output_path

if __name__ == "__main__":
    print("\n=== Creating New Shapes Visual Showcase ===\n")
    create_showcase()
