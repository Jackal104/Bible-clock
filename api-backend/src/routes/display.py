from flask import Blueprint, request, jsonify, send_file
import os
import subprocess
from pathlib import Path
import tempfile

display_bp = Blueprint('display', __name__)

# Path to the Bible Clock
BIBLE_CLOCK_PATH = '/home/ubuntu/bible-clock-enhanced'

@display_bp.route('/display/test', methods=['POST'])
def test_display():
    """Test the display with current configuration"""
    try:
        # Run the test script
        result = subprocess.run(
            ['python', 'bin/run_clock.py', '--once', '--simulate'],
            cwd=BIBLE_CLOCK_PATH,
            capture_output=True,
            text=True
        )
        
        # Find the generated image
        import glob
        images = glob.glob('/tmp/bible_clock_display_*.png')
        if images:
            latest_image = max(images, key=os.path.getctime)
            return jsonify({
                'success': True,
                'image_path': latest_image,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No display image generated',
                'output': result.stdout,
                'stderr': result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@display_bp.route('/display/preview')
def get_preview():
    """Get the latest display preview image"""
    try:
        import glob
        images = glob.glob('/tmp/bible_clock_display_*.png')
        if images:
            latest_image = max(images, key=os.path.getctime)
            return send_file(latest_image, mimetype='image/png')
        else:
            return jsonify({'error': 'No preview image available'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@display_bp.route('/display/status', methods=['GET'])
def get_status():
    """Get Bible Clock service status"""
    try:
        # Check if service is running
        result = subprocess.run(
            ['systemctl', 'is-active', 'bible-clock.service'],
            capture_output=True,
            text=True
        )
        
        service_active = result.returncode == 0 and result.stdout.strip() == 'active'
        
        # Get service status details
        status_result = subprocess.run(
            ['systemctl', 'status', 'bible-clock.service', '--no-pager'],
            capture_output=True,
            text=True
        )
        
        # Get memory usage if process is running
        memory_usage = 0
        try:
            ps_result = subprocess.run(
                ['pgrep', '-f', 'run_clock.py'],
                capture_output=True,
                text=True
            )
            if ps_result.returncode == 0:
                pid = ps_result.stdout.strip()
                if pid:
                    mem_result = subprocess.run(
                        ['ps', '-p', pid, '-o', 'rss='],
                        capture_output=True,
                        text=True
                    )
                    if mem_result.returncode == 0:
                        memory_usage = int(mem_result.stdout.strip()) // 1024  # Convert to MB
        except:
            pass
        
        return jsonify({
            'service_active': service_active,
            'memory_usage_mb': memory_usage,
            'status_output': status_result.stdout,
            'last_update': 'Unknown'  # Would need to read from log file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@display_bp.route('/display/restart', methods=['POST'])
def restart_service():
    """Restart the Bible Clock service"""
    try:
        result = subprocess.run(
            ['sudo', 'systemctl', 'restart', 'bible-clock.service'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

