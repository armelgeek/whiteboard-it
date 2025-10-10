#!/usr/bin/env python3
"""Test script for new geometric shapes (curved arrows, braces, sketchy shapes)."""

import sys
import cv2
import numpy as np
from whiteboard_animator import render_shape_to_image

def test_curved_arrow_quadratic():
    """Test curved arrow with quadratic bezier."""
    print("Testing curved arrow (quadratic bezier)...")
    
    shape_config = {
        "shape": "curved_arrow",
        "color": (0, 0, 0),  # Black in BGR
        "fill_color": (100, 100, 100),  # Gray fill for arrow head
        "stroke_width": 3,
        "curve_type": "quadratic",
        "points": [[100, 400], [400, 100], [700, 400]],  # Start, control, end
        "arrow_size": 30,
        "num_segments": 50
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Curved arrow (quadratic) rendering successful")
        cv2.imwrite("/tmp/test_curved_arrow_quadratic.png", img)
        return True
    else:
        print("✗ Curved arrow (quadratic) rendering failed")
        return False

def test_curved_arrow_cubic():
    """Test curved arrow with cubic bezier."""
    print("Testing curved arrow (cubic bezier)...")
    
    shape_config = {
        "shape": "curved_arrow",
        "color": (255, 0, 0),  # Blue in BGR
        "fill_color": (255, 150, 150),  # Light blue fill
        "stroke_width": 3,
        "curve_type": "cubic",
        "points": [[100, 300], [300, 100], [500, 100], [700, 300]],  # 4 control points
        "arrow_size": 30,
        "num_segments": 50
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Curved arrow (cubic) rendering successful")
        cv2.imwrite("/tmp/test_curved_arrow_cubic.png", img)
        return True
    else:
        print("✗ Curved arrow (cubic) rendering failed")
        return False

def test_brace_left():
    """Test left-facing brace."""
    print("Testing left brace...")
    
    shape_config = {
        "shape": "brace",
        "color": (0, 0, 0),  # Black in BGR
        "stroke_width": 3,
        "orientation": "left",
        "position": {"x": 200, "y": 300},
        "width": 30,
        "height": 200
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Left brace rendering successful")
        cv2.imwrite("/tmp/test_brace_left.png", img)
        return True
    else:
        print("✗ Left brace rendering failed")
        return False

def test_brace_right():
    """Test right-facing brace."""
    print("Testing right brace...")
    
    shape_config = {
        "shape": "brace",
        "color": (0, 128, 0),  # Green in BGR
        "stroke_width": 3,
        "orientation": "right",
        "position": {"x": 600, "y": 300},
        "width": 30,
        "height": 200
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Right brace rendering successful")
        cv2.imwrite("/tmp/test_brace_right.png", img)
        return True
    else:
        print("✗ Right brace rendering failed")
        return False

def test_brace_top():
    """Test top-facing brace."""
    print("Testing top brace...")
    
    shape_config = {
        "shape": "brace",
        "color": (128, 0, 128),  # Purple in BGR
        "stroke_width": 3,
        "orientation": "top",
        "position": {"x": 400, "y": 150},
        "width": 200,
        "height": 30
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Top brace rendering successful")
        cv2.imwrite("/tmp/test_brace_top.png", img)
        return True
    else:
        print("✗ Top brace rendering failed")
        return False

def test_brace_bottom():
    """Test bottom-facing brace."""
    print("Testing bottom brace...")
    
    shape_config = {
        "shape": "brace",
        "color": (0, 128, 128),  # Teal in BGR
        "stroke_width": 3,
        "orientation": "bottom",
        "position": {"x": 400, "y": 450},
        "width": 200,
        "height": 30
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Bottom brace rendering successful")
        cv2.imwrite("/tmp/test_brace_bottom.png", img)
        return True
    else:
        print("✗ Bottom brace rendering failed")
        return False

def test_sketchy_rectangle():
    """Test sketchy/hand-drawn rectangle."""
    print("Testing sketchy rectangle...")
    
    shape_config = {
        "shape": "sketchy_rectangle",
        "color": (0, 0, 0),  # Black in BGR
        "stroke_width": 2,
        "position": {"x": 400, "y": 300},
        "width": 300,
        "height": 200,
        "roughness": 3,
        "iterations": 3
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Sketchy rectangle rendering successful")
        cv2.imwrite("/tmp/test_sketchy_rectangle.png", img)
        return True
    else:
        print("✗ Sketchy rectangle rendering failed")
        return False

def test_sketchy_circle():
    """Test sketchy/hand-drawn circle."""
    print("Testing sketchy circle...")
    
    shape_config = {
        "shape": "sketchy_circle",
        "color": (0, 0, 255),  # Red in BGR
        "stroke_width": 2,
        "position": {"x": 400, "y": 300},
        "size": 120,
        "roughness": 3,
        "iterations": 3
    }
    
    img = render_shape_to_image(shape_config, 800, 600)
    
    if img is not None and img.shape == (600, 800, 3):
        print("✓ Sketchy circle rendering successful")
        cv2.imwrite("/tmp/test_sketchy_circle.png", img)
        return True
    else:
        print("✗ Sketchy circle rendering failed")
        return False

def test_combined_scene():
    """Test a combined scene with multiple new shapes."""
    print("Testing combined scene with new shapes...")
    
    # Create a blank canvas
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Add curved arrow
    shape1 = render_shape_to_image({
        "shape": "curved_arrow",
        "color": (255, 0, 0),
        "stroke_width": 3,
        "curve_type": "quadratic",
        "points": [[100, 500], [400, 200], [700, 500]],
        "arrow_size": 25
    }, 800, 600)
    
    # Add brace
    shape2 = render_shape_to_image({
        "shape": "brace",
        "color": (0, 0, 0),
        "stroke_width": 2,
        "orientation": "left",
        "position": {"x": 150, "y": 300},
        "width": 25,
        "height": 150
    }, 800, 600)
    
    # Add sketchy rectangle
    shape3 = render_shape_to_image({
        "shape": "sketchy_rectangle",
        "color": (0, 128, 0),
        "stroke_width": 2,
        "position": {"x": 400, "y": 100},
        "width": 200,
        "height": 80,
        "roughness": 2
    }, 800, 600)
    
    # Combine shapes (simple overlay - take non-white pixels)
    for shape in [shape1, shape2, shape3]:
        if shape is not None:
            mask = np.all(shape < 250, axis=2)
            img[mask] = shape[mask]
    
    cv2.imwrite("/tmp/test_combined_scene.png", img)
    print("✓ Combined scene rendering successful")
    return True

if __name__ == "__main__":
    print("\n=== Testing New Geometric Shapes Feature ===\n")
    
    tests = [
        test_curved_arrow_quadratic,
        test_curved_arrow_cubic,
        test_brace_left,
        test_brace_right,
        test_brace_top,
        test_brace_bottom,
        test_sketchy_rectangle,
        test_sketchy_circle,
        test_combined_scene
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {failed} test(s) failed")
        sys.exit(1)
