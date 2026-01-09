#!/bin/bash
# Omega System Startup Script for Unix/Mac

cd "$(dirname "$0")"
echo ""
echo "========================================"
echo "  OMEGA SYSTEM - STARTING"
echo "========================================"
echo ""
echo "Starting Omega Full Brain (Voice + Emotion)..."
echo "Press Ctrl+C to stop"
echo ""
python3 omega_full_brain.py
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Omega failed to start"
    echo "Check error messages above"
    exit 1
fi
