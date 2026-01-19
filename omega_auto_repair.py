"""
Omega Auto-Repair System
========================
Automatically detects and fixes common issues:
- Source control cleanup (auto-commit/stash changes)
- Missing dependencies installation
- File permission fixes
- Service restarts on crash
- Configuration validation
- Icon generation if missing

Runs continuously in background, monitoring system health.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

class OmegaAutoRepair:
    """Continuously monitors and repairs Omega system issues"""
    
    def __init__(self, workspace_path="H:\\The Gatekeeper"):
        self.workspace = Path(workspace_path)
        self.log_file = self.workspace / "auto_repair.log"
        self.repair_count = 0
        
    def log(self, message):
        """Log repair actions"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    
    def run_command(self, cmd, cwd=None):
        """Execute shell command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def fix_source_control(self):
        """Auto-commit or stash uncommitted changes"""
        self.log("[Source Control] Checking for uncommitted changes...")
        
        success, stdout, _ = self.run_command("git status --porcelain")
        if not success or not stdout.strip():
            return  # No changes or git error
        
        changes = stdout.strip().split('\n')
        if len(changes) == 0:
            return
        
        self.log(f"[Source Control] Found {len(changes)} uncommitted changes")
        
        self.log("[Source Control] Auto-committing changes...")
        self.run_command("git add -A")
        
        commit_msg = f"auto: Auto-repair commit - {len(changes)} files modified"
        success, _, _ = self.run_command(f'git commit -m "{commit_msg}"')
        
        if success:
            self.log(f"[Source Control] ✅ Auto-committed {len(changes)} changes")
            self.repair_count += 1
        else:
            self.log("[Source Control] Commit failed, stashing changes...")
            success, _, _ = self.run_command("git stash save 'Auto-repair stash'")
            if success:
                self.log("[Source Control] ✅ Stashed uncommitted changes")
                self.repair_count += 1
    
    def check_dependencies(self):
        """Verify required Python packages are installed"""
        required = [
            'flask',
            'flask_socketio',
            'flask_cors',
            'qrcode',
            'pillow',
            'psutil'
        ]
        
        missing = []
        for package in required:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.log(f"[Dependencies] Missing packages: {', '.join(missing)}")
            self.log("[Dependencies] Installing missing packages...")
            
            venv_python = self.workspace / ".venv" / "Scripts" / "python.exe"
            if venv_python.exists():
                cmd = f'"{venv_python}" -m pip install {" ".join(missing)}'
                success, _, _ = self.run_command(cmd)
                if success:
                    self.log(f"[Dependencies] ✅ Installed {len(missing)} packages")
                    self.repair_count += 1
    
    def check_icons(self):
        """Generate missing PWA icons"""
        icons_dir = self.workspace / "static" / "icons"
        required_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
        
        missing = []
        for size in required_sizes:
            icon_file = icons_dir / f"icon-{size}x{size}.png"
            if not icon_file.exists():
                missing.append(size)
        
        if missing:
            self.log(f"[Icons] Missing {len(missing)} icon sizes")
            self.log("[Icons] Generating missing icons...")
            
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                icons_dir.mkdir(parents=True, exist_ok=True)
                
                for size in missing:
                    icon = self._create_kitt_icon(size)
                    icon_file = icons_dir / f"icon-{size}x{size}.png"
                    icon.save(icon_file, 'PNG')
                
                self.log(f"[Icons] ✅ Generated {len(missing)} icons")
                self.repair_count += 1
            except ImportError:
                self.log("[Icons] ⚠️ Pillow not available, skipping icon generation")
    
    def _create_kitt_icon(self, size):
        """Create KITT-themed icon"""
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (size, size), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bar_height = size // 8
        bar_spacing = size // 12
        bar_width = size - (size // 4)
        start_x = (size - bar_width) // 2
        
        for i in range(3):
            y = (size // 2) - bar_height - bar_spacing + (i * bar_spacing)
            draw.rectangle(
                [start_x, y, start_x + bar_width, y + bar_height],
                fill=(255, 0, 0)
            )
        
        border_width = max(2, size // 64)
        draw.rectangle(
            [0, 0, size - 1, size - 1],
            outline=(255, 0, 0),
            width=border_width
        )
        
        return img
    
    def check_services(self):
        """Verify Omega services are running"""
        success, stdout, _ = self.run_command("tasklist | findstr python.exe")
        
        if success and "python.exe" in stdout.lower():
            return
        
        self.log("[Services] Omega PWA not running")
        self.log("[Services] Attempting to restart...")
        
        venv_python = self.workspace / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            script = self.workspace / "omega_pwa_kitt_ui.py"
            if script.exists():
                cmd = f'start /B "" "{venv_python}" "{script}"'
                success, _, _ = self.run_command(cmd)
                if success:
                    self.log("[Services] ✅ Restarted Omega PWA")
                    self.repair_count += 1
    
    def validate_config(self):
        """Validate configuration files"""
        manifest_file = self.workspace / "static" / "manifest.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
                for field in required_fields:
                    if field not in data:
                        self.log(f"[Config] ⚠️ manifest.json missing '{field}'")
            except json.JSONDecodeError:
                self.log("[Config] ⚠️ manifest.json is corrupted")
    
    def run_repair_cycle(self):
        """Run one complete repair cycle"""
        self.log("=" * 60)
        self.log("[Auto-Repair] Starting repair cycle...")
        
        start_time = time.time()
        self.repair_count = 0
        
        self.fix_source_control()
        self.check_dependencies()
        self.check_icons()
        self.check_services()
        self.validate_config()
        
        elapsed = time.time() - start_time
        self.log(f"[Auto-Repair] Cycle complete in {elapsed:.2f}s - {self.repair_count} repairs made")
        self.log("=" * 60)
    
    def run_continuous(self, interval=30):
        """Run continuous monitoring loop"""
        self.log("[Auto-Repair] Starting continuous monitoring...")
        self.log(f"[Auto-Repair] Check interval: {interval} seconds")
        self.log(f"[Auto-Repair] Workspace: {self.workspace}")
        
        try:
            while True:
                self.run_repair_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.log("[Auto-Repair] Stopped by user")

def main():
    print("=" * 70)
    print("           OMEGA AUTO-REPAIR SYSTEM")
    print("=" * 70)
    print()
    print("Monitors and automatically fixes:")
    print("  • Source control issues (auto-commit/stash)")
    print("  • Missing dependencies")
    print("  • Missing PWA icons")
    print("  • Service crashes")
    print("  • Configuration problems")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    repair_system = OmegaAutoRepair()
    
    repair_system.run_repair_cycle()
    
    print()
    response = input("Start continuous monitoring? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n[Auto-Repair] Starting continuous monitoring (30 second intervals)...")
        repair_system.run_continuous(interval=30)
    else:
        print("[Auto-Repair] Single repair cycle complete. Exiting.")

if __name__ == "__main__":
    main()
