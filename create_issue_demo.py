#!/usr/bin/env python3
"""
Demo showcasing all new shapes with visual examples matching the issue requirements.
This script demonstrates:
1. Curved arrows (fleche lineaire qu'on peu courbé)
2. Braces/accolades (forme geometrique accolade)
3. Hand-drawn framing rectangles (encadrer un layer avec du carré en dessinant)
4. Hand-drawn circles (forme d'entourage realiste fait a la main)
"""

import cv2
import numpy as np
from whiteboard_animator import render_shape_to_image

def create_issue_requirement_demo():
    """Create a demo showing all shapes requested in the issue."""
    
    # Create large canvas
    canvas_width = 1600
    canvas_height = 1200
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    
    print("\n=== Creating Issue Requirement Demo ===\n")
    
    # Section 1: Curved Arrows (fleche lineaire qu'on peu courbé)
    print("1. Creating curved arrows...")
    
    # Simple downward arc
    arrow1 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (0, 0, 0),
        "fill_color": (100, 100, 100),
        "stroke_width": 4,
        "curve_type": "quadratic",
        "points": [[150, 200], [400, 350], [650, 200]],
        "arrow_size": 35
    }, canvas_width, canvas_height)
    
    # S-curve arrow
    arrow2 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (0, 0, 0),
        "fill_color": (100, 100, 100),
        "stroke_width": 4,
        "curve_type": "cubic",
        "points": [[900, 150], [1000, 350], [1200, 150], [1400, 300]],
        "arrow_size": 35
    }, canvas_width, canvas_height)
    
    # Upward arc
    arrow3 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (0, 0, 0),
        "fill_color": (100, 100, 100),
        "stroke_width": 4,
        "curve_type": "quadratic",
        "points": [[150, 450], [400, 300], [650, 450]],
        "arrow_size": 35
    }, canvas_width, canvas_height)
    
    # Section 2: Braces/Accolades
    print("2. Creating braces (accolades)...")
    
    # Left brace
    brace1 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 0, 0),
        "stroke_width": 3,
        "orientation": "left",
        "position": {"x": 950, "y": 650},
        "width": 40,
        "height": 280
    }, canvas_width, canvas_height)
    
    # Right brace
    brace2 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 0, 0),
        "stroke_width": 3,
        "orientation": "right",
        "position": {"x": 1450, "y": 650},
        "width": 40,
        "height": 280
    }, canvas_width, canvas_height)
    
    # Section 3: Hand-drawn framing rectangles
    print("3. Creating hand-drawn framing rectangles...")
    
    # Sketchy rectangle to frame text "7 ans"
    rect1 = render_shape_to_image({
        "shape": "sketchy_rectangle",
        "color": (0, 0, 0),
        "stroke_width": 2,
        "position": {"x": 300, "y": 950},
        "width": 200,
        "height": 100,
        "roughness": 3,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Another framing rectangle
    rect2 = render_shape_to_image({
        "shape": "sketchy_rectangle",
        "color": (0, 0, 0),
        "stroke_width": 2,
        "position": {"x": 700, "y": 950},
        "width": 250,
        "height": 120,
        "roughness": 4,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Section 4: Hand-drawn circles for encircling
    print("4. Creating hand-drawn circles (realistic encircling)...")
    
    # Circle around "Jour 20"
    circle1 = render_shape_to_image({
        "shape": "sketchy_circle",
        "color": (0, 0, 255),  # Red in BGR
        "stroke_width": 2,
        "position": {"x": 1200, "y": 950},
        "size": 80,
        "roughness": 3,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Another encircling
    circle2 = render_shape_to_image({
        "shape": "sketchy_circle",
        "color": (0, 0, 255),  # Red in BGR
        "stroke_width": 2,
        "position": {"x": 1400, "y": 950},
        "size": 90,
        "roughness": 4,
        "iterations": 3
    }, canvas_width, canvas_height)
    
    # Combine all shapes
    print("5. Combining shapes on canvas...")
    shapes = [arrow1, arrow2, arrow3, brace1, brace2, rect1, rect2, circle1, circle2]
    
    for shape in shapes:
        if shape is not None:
            mask = np.all(shape < 250, axis=2)
            canvas[mask] = shape[mask]
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Title
    cv2.putText(canvas, "New Shapes - Issue Requirements Demo", (450, 50), font, 1.2, (0, 0, 0), 2)
    
    # Section labels
    cv2.putText(canvas, "1. Curved Arrows (fleches courbes)", (100, 120), font, 0.8, (0, 0, 0), 2)
    cv2.putText(canvas, "Downward arc", (300, 380), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "S-curve", (1100, 380), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Upward arc", (300, 530), font, 0.6, (100, 100, 100), 1)
    
    cv2.putText(canvas, "2. Braces (accolades)", (1050, 570), font, 0.8, (0, 0, 0), 2)
    cv2.putText(canvas, "Left", (880, 800), font, 0.6, (100, 100, 100), 1)
    cv2.putText(canvas, "Right", (1450, 800), font, 0.6, (100, 100, 100), 1)
    
    cv2.putText(canvas, "3. Hand-drawn Framing Rectangles", (100, 870), font, 0.8, (0, 0, 0), 2)
    cv2.putText(canvas, "7 ans", (250, 955), font, 0.8, (100, 50, 200), 2)
    cv2.putText(canvas, "Example text", (620, 955), font, 0.8, (100, 50, 200), 2)
    
    cv2.putText(canvas, "4. Realistic Encircling (hand-drawn)", (1000, 870), font, 0.8, (0, 0, 0), 2)
    cv2.putText(canvas, "Jour 20", (1160, 955), font, 0.7, (100, 50, 200), 2)
    cv2.putText(canvas, "Item", (1370, 955), font, 0.7, (100, 50, 200), 2)
    
    # Footer
    cv2.putText(canvas, "All shapes support progressive drawing animation, colors, and styling", 
                (300, 1150), font, 0.7, (100, 100, 100), 1)
    
    # Save
    output_path = "/tmp/issue_requirements_demo.png"
    cv2.imwrite(output_path, canvas)
    print(f"\n✓ Demo saved to {output_path}")
    
    # Also save to repo
    repo_path = "issue_requirements_demo.png"
    cv2.imwrite(repo_path, canvas)
    print(f"✓ Demo also saved to {repo_path}")
    
    return output_path

if __name__ == "__main__":
    create_issue_requirement_demo()
    print("\n=== Demo Complete ===\n")
