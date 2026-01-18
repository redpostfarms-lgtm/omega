#!/usr/bin/env python3
"""Test loading OMEGA Swarm HTML files"""
import os

EXTRACTED_PATH = os.path.join(os.path.dirname(__file__), 'extracted_files_4')

def load_html_file(filename):
    """Load HTML file from extracted directory"""
    try:
        filepath = os.path.join(EXTRACTED_PATH, filename)
        print(f"Loading: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Loaded {filename}: {len(content)} bytes")
        return content
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None

print("=" * 60)
print("Testing HTML file loading...")
print("=" * 60)

queen = load_html_file('queen.html')
drone = load_html_file('drone.html')

print()
print(f"Queen HTML: {len(queen) if queen else 0} bytes")
print(f"Drone HTML: {len(drone) if drone else 0} bytes")

if queen:
    print("\n✅ Queen HTML loaded successfully")
    # Check for external resources
    if 'manifest.json' in queen:
        print("⚠️  References manifest.json")
    if 'src=' in queen or 'href=' in queen:
        print("⚠️  Contains external resource references")

if drone:
    print("✅ Drone HTML loaded successfully")
