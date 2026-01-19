"""
Omega Download Manager
Automatically routes all downloads to H:\\The Gatekeeper\\downloads
Activates when Omega takes over desktop
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class OmegaDownloadManager:
    def __init__(self):
        self.base_dir = Path(r"H:\The Gatekeeper\downloads")
        self.modeling_tools_dir = self.base_dir / "modeling_tools"
        self.omega_resources_dir = self.base_dir / "omega_resources"
        self.config_file = self.base_dir / "download_config.json"

        # Ensure directories exist
        for dir_path in [self.base_dir, self.modeling_tools_dir, self.omega_resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.load_config()

    def load_config(self):
        """Load download configuration"""
        default_config = {
            "auto_sort": True,
            "modeling_extensions": [".gguf", ".safetensors", ".pt", ".pth", ".bin", ".onnx"],
            "omega_extensions": [".json", ".yaml", ".yml", ".conf", ".cfg"],
            "archive_extensions": [".zip", ".tar", ".gz", ".rar", ".7z"],
            "auto_categorize": True,
            "log_downloads": True,
            "desktop_takeover_active": False,
        }

        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save download configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def activate_desktop_takeover(self):
        """Activate Omega desktop takeover mode"""
        self.config["desktop_takeover_active"] = True
        self.save_config()
        print("🚀 Omega Desktop Takeover Mode: ACTIVATED")
        print(f"📥 Downloads routing to: {self.base_dir}")
        return True

    def deactivate_desktop_takeover(self):
        """Deactivate Omega desktop takeover mode"""
        self.config["desktop_takeover_active"] = False
        self.save_config()
        print("⏸️ Omega Desktop Takeover Mode: DEACTIVATED")
        return True

    def categorize_file(self, filename: str) -> Path:
        """Determine which directory a file should go to"""
        ext = Path(filename).suffix.lower()

        # Check for modeling tools
        if ext in self.config["modeling_extensions"]:
            return self.modeling_tools_dir

        # Check for Omega resources
        if ext in self.config["omega_extensions"]:
            return self.omega_resources_dir

        # Check filename patterns
        name_lower = filename.lower()
        if any(pattern in name_lower for pattern in ["omega", "gatekeeper"]):
            return self.omega_resources_dir

        if any(pattern in name_lower for pattern in ["model", "llm", "ai", "gguf", "safetensors"]):
            return self.modeling_tools_dir

        # Default to base downloads
        return self.base_dir

    def move_download(self, source_path: str, auto_categorize: bool = True) -> bool:
        """Move a downloaded file to appropriate directory"""
        source = Path(source_path)

        if not source.exists():
            print(f"❌ File not found: {source}")
            return False

        # Determine destination
        if auto_categorize and self.config["auto_categorize"]:
            dest_dir = self.categorize_file(source.name)
        else:
            dest_dir = self.base_dir

        dest_path = dest_dir / source.name

        # Handle duplicates
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"

        # Move file
        try:
            shutil.move(str(source), str(dest_path))
            print(f"✅ Moved: {source.name}")
            print(f"   → {dest_path.parent.name}/")

            # Log download
            if self.config["log_downloads"]:
                self.log_download(source.name, str(dest_path))

            return True
        except Exception as e:
            print(f"❌ Error moving {source.name}: {e}")
            return False

    def log_download(self, filename: str, destination: str) -> None:
        """Log download activity"""
        log_file = self.base_dir / "download_log.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {filename} → {destination}\n")

    def scan_user_downloads(self) -> List[Path]:
        """Scan user Downloads folder for Omega-related files"""
        user_downloads = Path.home() / "Downloads"

        if not user_downloads.exists():
            print("❌ User Downloads folder not found")
            return []

        omega_patterns = ["omega", "gatekeeper", "model", "llm", "ai", "gguf", "safetensors"]
        found_files = []

        for file in user_downloads.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if any(pattern in name_lower for pattern in omega_patterns):
                    found_files.append(file)

        return found_files

    def import_user_downloads(self):
        """Import Omega-related files from user Downloads"""
        files = self.scan_user_downloads()

        if not files:
            print("✅ No Omega-related files in user Downloads")
            return 0

        print(f"\n📥 Found {len(files)} file(s) to import:")
        moved_count = 0

        for file in files:
            print(f"\n  {file.name}")
            if self.move_download(file):
                moved_count += 1

        print(f"\n✅ Imported {moved_count}/{len(files)} files")
        return moved_count

    def get_status(self):
        """Get current download manager status"""
        status = {
            "Base Directory": str(self.base_dir),
            "Desktop Takeover": "ACTIVE" if self.config["desktop_takeover_active"] else "INACTIVE",
            "Auto-Categorize": "ON" if self.config["auto_categorize"] else "OFF",
            "Auto-Sort": "ON" if self.config["auto_sort"] else "OFF",
            "Download Logging": "ON" if self.config["log_downloads"] else "OFF",
            "Modeling Tools Dir": str(self.modeling_tools_dir),
            "Omega Resources Dir": str(self.omega_resources_dir),
        }
        return status

    def print_status(self):
        """Print current status"""
        print("\n" + "=" * 60)
        print("📥 OMEGA DOWNLOAD MANAGER STATUS")
        print("=" * 60)

        status = self.get_status()
        for key, value in status.items():
            print(f"{key:.<30} {value}")

        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    manager = OmegaDownloadManager()

    print("🔧 Omega Download Manager")
    print("=" * 60)

    # Show status
    manager.print_status()

    # Check for files to import
    print("🔍 Scanning user Downloads folder...")
    files = manager.scan_user_downloads()

    if files:
        print(f"\n📦 Found {len(files)} Omega-related file(s):")
        for file in files:
            print(f"  • {file.name}")

        response = input("\nImport these files? (y/n): ").lower().strip()
        if response == "y":
            manager.import_user_downloads()
    else:
        print("✅ No files to import")

    # Activation prompt
    if not manager.config["desktop_takeover_active"]:
        print("\n" + "=" * 60)
        print("🚀 OMEGA DESKTOP TAKEOVER")
        print("=" * 60)
        print("When activated, all downloads will route to:")
        print(f"  {manager.base_dir}")
        print("\nReady to activate? This will redirect all downloads.")

        response = input("Activate Desktop Takeover Mode? (y/n): ").lower().strip()
        if response == "y":
            manager.activate_desktop_takeover()
        else:
            print("⏸️ Desktop Takeover Mode remains inactive")
    else:
        print("\n✅ Desktop Takeover Mode is ACTIVE")
        response = input("Deactivate? (y/n): ").lower().strip()
        if response == "y":
            manager.deactivate_desktop_takeover()


if __name__ == "__main__":
    main()
