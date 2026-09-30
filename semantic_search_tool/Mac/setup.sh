#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

echo "=========================================="
echo "       Finder App - Mac Installer      "
echo "=========================================="

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found!"
    echo "Please install Python 3 (e.g., install Xcode tools or download from python.org)"
    exit 1
fi
echo "[OK] Python 3 found."

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment already exists. Skipping creation."
fi

# 3. Install Dependencies
echo "[INFO] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Permissions
echo "[INFO] Setting permissions..."
chmod +x run_finder.command
chmod +x install_autostart.sh

echo ""
echo "=========================================="
echo "        Installation Complete!            "
echo "=========================================="
echo ""
echo "1. To start the app, double-click 'run_finder.command'."
echo "2. To enable auto-start on login, run './install_autostart.sh'."
echo ""
