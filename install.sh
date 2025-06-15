#!/bin/bash

# Bible Clock Enhanced - Installation Script
# This script installs the Bible Clock Enhanced package on a Raspberry Pi

set -e

echo "=== Bible Clock Enhanced Installation ==="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Installation will continue but hardware features may not work"
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please do not run this script as root"
    echo "   Run as regular user: ./install.sh"
    exit 1
fi

# Variables
INSTALL_DIR="/home/$(whoami)/bible-clock-enhanced"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_FILE="bible-clock.service"

echo "📁 Installation directory: $INSTALL_DIR"

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Bible Clock Enhanced directory not found: $INSTALL_DIR"
    echo "   Please extract the package first"
    exit 1
fi

cd "$INSTALL_DIR"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y python3-venv python3-pip git

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment and install dependencies
echo "📚 Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.template .env
    echo "   Please edit .env file to configure your settings"
fi

# Validate configuration
echo "✅ Validating configuration..."
python bin/validate_config.py

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp "systemd/$SERVICE_FILE" "/etc/systemd/system/"

# Update service file paths
sudo sed -i "s|/home/pi/bible-clock-enhanced|$INSTALL_DIR|g" "/etc/systemd/system/$SERVICE_FILE"
sudo sed -i "s|User=pi|User=$(whoami)|g" "/etc/systemd/system/$SERVICE_FILE"

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_FILE"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file to configure your display settings"
echo "   2. Test the installation: python bin/run_clock.py --test"
echo "   3. Start the service: sudo systemctl start bible-clock.service"
echo "   4. Monitor the service: ./bin/monitor_service.sh"
echo ""
echo "📖 For more information, see README.md"

