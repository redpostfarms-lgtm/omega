"""
Omega Quick Start - Load and Test System
"""

import warnings

warnings.filterwarnings("ignore")

from omega_system_access import omega

print("\n" + "=" * 60)
print("🚀 OMEGA SYSTEM - QUICK START")
print("=" * 60)

creds = omega.get_credentials()
print(f"\n👤 User: {creds['user']}")
print(f"📧 Email: {creds['email']}")

status = omega.system_status()
print(f"\n📦 Installed Packages: {status['total_packages']}")
print(f"🎯 Categories: {', '.join(status['categories'])}")

print(f"\n✨ Available Capabilities ({len(status['capabilities'])}):")
for i, cap in enumerate(sorted(status["capabilities"])[:10], 1):
    print(f"   {i}. {cap}")
if len(status["capabilities"]) > 10:
    print(f"   ... and {len(status['capabilities']) - 10} more")

print("\n" + "=" * 60)
print("✅ OMEGA IS READY TO GO!")
print("=" * 60)
print("\n💡 Usage Examples:")
print("   from omega_system_access import omega")
print("   omega.get_ai_client('openai')  # Get OpenAI client")
print("   omega.create_web_app('fastapi')  # Create FastAPI app")
print("   omega.connect_database('redis')  # Connect to Redis")
print("\n")
