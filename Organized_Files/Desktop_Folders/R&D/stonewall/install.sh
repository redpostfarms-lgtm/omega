#!/bin/bash
# Stonewall VPN - One-line install script

echo "============================================================"
echo "STONEWALL VPN - Installation"
echo "============================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install cryptography requests

# Make executable
chmod +x stonewall_core.py

# Run setup
python3 -m stonewall.setup

echo ""
echo "✅ Stonewall installed!"
echo ""
echo "Usage:"
echo "  python3 -m stonewall.stonewall_core --init      # Start VPN"
echo "  python3 -m stonewall.stonewall_core --daemon    # Run as daemon"
echo "  python3 -m stonewall.stonewall_core --status    # Check status"
echo "  python3 -m stonewall.stonewall_core --stop      # Stop VPN"
echo ""
echo "🔒 Your machine is ready to go dark."

