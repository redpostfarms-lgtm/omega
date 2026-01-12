#!/usr/bin/env python3
"""
Test Matplotlib Display - Find Working Backend
===============================================
Tests different matplotlib backends to find one that displays a window.
"""

import sys

print("=" * 80)
print("TESTING MATPLOTLIB BACKENDS")
print("=" * 80)
print()

# Test TkAgg
print("[1/3] Testing TkAgg backend...")
try:
    import matplotlib
    matplotlib.use('TkAgg', force=True)
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, 'TkAgg Backend Test\nWindow Should Be Visible', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    ax.set_title('TkAgg Test Window')
    ax.axis('off')
    
    print("  ✓ TkAgg backend loaded")
    print("  Opening test window...")
    print("  If you see a window, TkAgg works!")
    print()
    print("  Close the window to continue...")
    
    plt.show(block=True)  # Block until window is closed
    plt.close(fig)
    
    print("  ✓ TkAgg backend works!")
    print()
    print("RECOMMENDATION: Use TkAgg backend")
    sys.exit(0)
    
except Exception as e:
    print(f"  ✗ TkAgg failed: {e}")
    print()

# Test Qt5Agg
print("[2/3] Testing Qt5Agg backend...")
try:
    import matplotlib
    matplotlib.use('Qt5Agg', force=True)
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, 'Qt5Agg Backend Test\nWindow Should Be Visible', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    ax.set_title('Qt5Agg Test Window')
    ax.axis('off')
    
    print("  ✓ Qt5Agg backend loaded")
    print("  Opening test window...")
    print("  If you see a window, Qt5Agg works!")
    print()
    print("  Close the window to continue...")
    
    plt.show(block=True)
    plt.close(fig)
    
    print("  ✓ Qt5Agg backend works!")
    print()
    print("RECOMMENDATION: Use Qt5Agg backend")
    sys.exit(0)
    
except Exception as e:
    print(f"  ✗ Qt5Agg failed: {e}")
    print()

# Test default
print("[3/3] Testing default backend...")
try:
    import matplotlib
    import matplotlib.pyplot as plt
    
    backend = matplotlib.get_backend()
    print(f"  Default backend: {backend}")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, f'Default Backend Test ({backend})\nWindow Should Be Visible', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    ax.set_title(f'Default Backend Test ({backend})')
    ax.axis('off')
    
    print("  Opening test window...")
    print("  If you see a window, default backend works!")
    print()
    print("  Close the window to continue...")
    
    plt.show(block=True)
    plt.close(fig)
    
    print(f"  ✓ Default backend ({backend}) works!")
    print()
    print(f"RECOMMENDATION: Use default backend ({backend})")
    sys.exit(0)
    
except Exception as e:
    print(f"  ✗ Default backend failed: {e}")
    print()

print("=" * 80)
print("NO WORKING BACKEND FOUND")
print("=" * 80)
print()
print("Install tkinter or PyQt5:")
print("  - tkinter usually comes with Python")
print("  - PyQt5: pip install PyQt5")
print()
sys.exit(1)
