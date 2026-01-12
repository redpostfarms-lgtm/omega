#!/usr/bin/env python3
from pathlib import Path
desktop = Path.home() / "Desktop"
share_folder = desktop / "Omega_UI_Images"
if share_folder.exists():
    files = list(share_folder.glob("*"))
    print(f"Found {len(files)} files in {share_folder}")
    for f in files:
        if f.is_file():
            print(f"  - {f.name} ({f.stat().st_size/1024:.1f} KB)")
else:
    print("Folder does not exist - running copy script...")
    import subprocess
    import sys
    subprocess.run([sys.executable, "COPY_UI_SCREENSHOTS.py"])
