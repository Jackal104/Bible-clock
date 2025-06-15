#!/bin/bash

# Bible Clock Enhanced - Service Monitoring Script
# This script monitors the Bible Clock service and provides status information

echo "=== Bible Clock Service Monitor ==="

# Check if service exists
if ! systemctl list-unit-files | grep -q "bible-clock.service"; then
    echo "❌ Bible Clock service not installed"
    echo ""
    echo "To install the service:"
    echo "  sudo cp systemd/bible-clock.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable bible-clock.service"
    exit 1
fi

# Service status
echo "📊 Service Status:"
sudo systemctl status bible-clock.service --no-pager -l

echo ""
echo "📈 Recent Log Entries:"
sudo journalctl -u bible-clock.service -n 10 --no-pager

echo ""
echo "💾 Resource Usage:"
PID=$(pgrep -f "run_clock.py")
if [ -n "$PID" ]; then
    echo "  Process ID: $PID"
    echo "  Memory: $(ps -p $PID -o rss= | awk '{print $1/1024 " MB"}')"
    echo "  CPU: $(ps -p $PID -o %cpu= | awk '{print $1"%"}')"
else
    echo "  Process not running"
fi

echo ""
echo "🔧 Quick Commands:"
echo "  Start:   sudo systemctl start bible-clock.service"
echo "  Stop:    sudo systemctl stop bible-clock.service"
echo "  Restart: sudo systemctl restart bible-clock.service"
echo "  Logs:    sudo journalctl -u bible-clock.service -f"

