"""
Omega Applications Manager
Moves large portable apps to H: drive and creates symbolic links
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


class OmegaAppsManager:
    def __init__(self):
        self.omega_apps = Path("H:/The Gatekeeper/omega_apps")
        self.log_file = Path("H:/The Gatekeeper/logs/omega_apps.log")

        # Create directories
        self.omega_apps.mkdir(parents=True, exist_ok=True)
        (self.omega_apps / "game_launchers").mkdir(exist_ok=True)
        (self.omega_apps / "development_tools").mkdir(exist_ok=True)
        (self.omega_apps / "utilities").mkdir(exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """Log activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(log_entry.strip())

    def get_folder_size(self, path):
        """Get total size of folder in MB"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self.get_folder_size(entry.path)
        except:
            pass
        return total / (1024 * 1024)  # Convert to MB

    def create_symlink(self, source, target):
        """Create symbolic link (requires admin)"""
        try:
            # Use mklink via cmd
            cmd = f'mklink /D "{target}" "{source}"'
            result = subprocess.run(["cmd", "/c", cmd], capture_output=True, text=True, shell=False)
            return result.returncode == 0
        except Exception as e:
            self.log(f"Error creating symlink: {e}")
            return False

    def move_app(self, source_path, dest_category, app_name):
        """Move application to omega_apps and create symlink"""
        source = Path(source_path)

        if not source.exists():
            self.log(f"⚠ Source not found: {source}")
            return False

        # Calculate size
        size_mb = self.get_folder_size(str(source))
        self.log(f"📦 Processing: {app_name} ({size_mb:.2f} MB)")

        # Destination
        dest = self.omega_apps / dest_category / app_name

        if dest.exists():
            self.log(f"⚠ Destination already exists: {dest}")
            return False

        try:
            # Move the folder
            self.log(f"🚚 Moving {app_name}...")
            shutil.move(str(source), str(dest))

            # Create symbolic link back
            self.log(f"🔗 Creating symbolic link...")
            success = self.create_symlink(str(dest), str(source))

            if success:
                self.log(f"✅ Successfully moved {app_name}")
                self.log(f"   Freed: {size_mb:.2f} MB from C: drive")
                return True
            else:
                # Rollback if symlink failed
                self.log(f"⚠ Symlink failed, rolling back...")
                shutil.move(str(dest), str(source))
                return False

        except Exception as e:
            self.log(f"❌ Error moving {app_name}: {e}")
            return False

    def scan_moveable_apps(self):
        """Scan for apps that can be moved"""
        moveable = []

        apps_to_check = [
            ("C:/Program Files (x86)/Glyph", "game_launchers", "Glyph"),
            ("C:/Program Files (x86)/Battle.net", "game_launchers", "Battle.net"),
            ("C:/Program Files/cursor", "development_tools", "cursor"),
            ("C:/Program Files/Git", "development_tools", "Git"),
        ]

        for source, category, name in apps_to_check:
            if Path(source).exists():
                size = self.get_folder_size(source)
                moveable.append(
                    {
                        "name": name,
                        "source": source,
                        "category": category,
                        "size_mb": size,
                        "size_gb": size / 1024,
                    }
                )

        return moveable

    def create_omega_integration(self):
        """Create integration file for Omega"""
        integration = self.omega_apps / "OMEGA_INTEGRATION.json"

        import json

        data = {
            "omega_apps_path": str(self.omega_apps),
            "description": "Centralized application storage for Omega system",
            "categories": {
                "game_launchers": "Gaming platform launchers (Glyph, Battle.net, Steam)",
                "development_tools": "Development and coding tools",
                "utilities": "System utilities and tools",
            },
            "integration_notes": [
                "All apps linked via symbolic links from original locations",
                "Omega can access apps through H:/The Gatekeeper/omega_apps",
                "Original paths maintained for compatibility",
                "Space saved on C: drive while maintaining functionality",
            ],
            "setup_date": datetime.now().isoformat(),
        }

        with open(integration, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.log(f"📄 Created integration file: {integration}")

    def generate_report(self):
        """Generate report of moved apps"""
        report = []
        report.append("=" * 60)
        report.append("OMEGA APPLICATIONS REPORT")
        report.append("=" * 60)

        total_size = 0

        for category in ["game_launchers", "development_tools", "utilities"]:
            cat_path = self.omega_apps / category
            if cat_path.exists():
                apps = list(cat_path.iterdir())
                if apps:
                    report.append(f"\n{category.replace('_', ' ').title()}:")
                    for app in apps:
                        if app.is_dir():
                            size = self.get_folder_size(str(app))
                            total_size += size
                            report.append(f"  • {app.name}: {size:.2f} MB")

        report.append(f"\nTotal space managed: {total_size:.2f} MB ({total_size / 1024:.2f} GB)")
        report.append("=" * 60)

        report_text = "\n".join(report)
        print(report_text)

        # Save report
        report_file = self.omega_apps / "APPS_REPORT.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_text)

        return total_size


def main():
    print("\n" + "=" * 60)
    print("🤖 OMEGA APPLICATIONS MANAGER")
    print("=" * 60)

    manager = OmegaAppsManager()

    # Scan for moveable apps
    print("\n🔍 Scanning for moveable applications...")
    moveable = manager.scan_moveable_apps()

    if not moveable:
        print("\n✅ No moveable apps found (already organized)")
        return

    print(f"\n📦 Found {len(moveable)} moveable applications:")
    total_size_gb = 0
    for app in moveable:
        print(f"  • {app['name']}: {app['size_gb']:.2f} GB")
        total_size_gb += app["size_gb"]

    print(f"\n💾 Total space to free: {total_size_gb:.2f} GB")

    response = input("\n⚠ REQUIRES ADMINISTRATOR RIGHTS\nMove apps? (y/n): ").lower().strip()

    if response != "y":
        print("\nOperation cancelled.")
        return

    print("\n" + "=" * 60)
    print("🚀 MOVING APPLICATIONS")
    print("=" * 60)

    moved_count = 0
    freed_mb = 0

    for app in moveable:
        success = manager.move_app(app["source"], app["category"], app["name"])
        if success:
            moved_count += 1
            freed_mb += app["size_mb"]

    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Moved {moved_count}/{len(moveable)} applications")
    print(f"💾 Freed: {freed_mb / 1024:.2f} GB from C: drive")
    print("=" * 60)

    # Create integration file
    manager.create_omega_integration()

    # Generate report
    manager.generate_report()


if __name__ == "__main__":
    main()
