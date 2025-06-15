from flask import Blueprint, request, jsonify
import os
import json
from pathlib import Path

config_bp = Blueprint('config', __name__)

# Path to the Bible Clock configuration
BIBLE_CLOCK_PATH = '/home/ubuntu/bible-clock-enhanced'
CONFIG_FILE = os.path.join(BIBLE_CLOCK_PATH, '.env')

@config_bp.route('/config', methods=['GET'])
def get_config():
    """Get current Bible Clock configuration"""
    try:
        config = {}
        
        # Read .env file if it exists
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        
        # Convert to frontend format
        frontend_config = {
            'displayWidth': int(config.get('DISPLAY_WIDTH', 1872)),
            'displayHeight': int(config.get('DISPLAY_HEIGHT', 1404)),
            'vcomValue': float(config.get('VCOM_VALUE', -1.50)),
            'simulationMode': config.get('SIMULATION_MODE', 'false').lower() == 'true',
            'bibleVersion': config.get('BIBLE_VERSION', 'kjv'),
            'fallbackEnabled': config.get('FALLBACK_ENABLED', 'true').lower() == 'true',
            'updateInterval': int(config.get('UPDATE_INTERVAL', 60)),
            'startupDelay': int(config.get('STARTUP_DELAY', 30)),
            'defaultFontSize': int(config.get('DEFAULT_FONT_SIZE', 48)),
            'titleFontSize': int(config.get('TITLE_FONT_SIZE', 36)),
            'fontFamily': config.get('FONT_FAMILY', 'DejaVu Sans'),
            'backgroundType': config.get('BACKGROUND_TYPE', 'solid'),
            'backgroundColor': config.get('BACKGROUND_COLOR', '#FFFFFF'),
            'backgroundImage': config.get('BACKGROUND_IMAGE', ''),
            'backgroundOpacity': float(config.get('BACKGROUND_OPACITY', 0.1)),
            'memoryLimit': int(config.get('MEMORY_LIMIT_MB', 100)),
            'refreshOptimization': config.get('REFRESH_OPTIMIZATION', 'true').lower() == 'true',
            'fullRefreshInterval': int(config.get('FULL_REFRESH_INTERVAL', 10)),
            'logLevel': config.get('LOG_LEVEL', 'INFO'),
            'debugMode': config.get('DEBUG_MODE', 'false').lower() == 'true'
        }
        
        return jsonify(frontend_config)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config', methods=['POST'])
def save_config():
    """Save Bible Clock configuration"""
    try:
        data = request.get_json()
        
        # Convert frontend format to .env format
        env_config = {
            'DISPLAY_WIDTH': str(data.get('displayWidth', 1872)),
            'DISPLAY_HEIGHT': str(data.get('displayHeight', 1404)),
            'VCOM_VALUE': str(data.get('vcomValue', -1.50)),
            'SIMULATION_MODE': str(data.get('simulationMode', False)).lower(),
            'BIBLE_VERSION': data.get('bibleVersion', 'kjv'),
            'FALLBACK_ENABLED': str(data.get('fallbackEnabled', True)).lower(),
            'UPDATE_INTERVAL': str(data.get('updateInterval', 60)),
            'STARTUP_DELAY': str(data.get('startupDelay', 30)),
            'DEFAULT_FONT_SIZE': str(data.get('defaultFontSize', 48)),
            'TITLE_FONT_SIZE': str(data.get('titleFontSize', 36)),
            'FONT_FAMILY': data.get('fontFamily', 'DejaVu Sans'),
            'BACKGROUND_TYPE': data.get('backgroundType', 'solid'),
            'BACKGROUND_COLOR': data.get('backgroundColor', '#FFFFFF'),
            'BACKGROUND_IMAGE': data.get('backgroundImage', ''),
            'BACKGROUND_OPACITY': str(data.get('backgroundOpacity', 0.1)),
            'MEMORY_LIMIT_MB': str(data.get('memoryLimit', 100)),
            'REFRESH_OPTIMIZATION': str(data.get('refreshOptimization', True)).lower(),
            'FULL_REFRESH_INTERVAL': str(data.get('fullRefreshInterval', 10)),
            'LOG_LEVEL': data.get('logLevel', 'INFO'),
            'DEBUG_MODE': str(data.get('debugMode', False)).lower()
        }
        
        # Read existing .env file to preserve other settings
        existing_config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_config[key] = value
        
        # Update with new values
        existing_config.update(env_config)
        
        # Write back to .env file
        with open(CONFIG_FILE, 'w') as f:
            f.write("# Bible Clock Enhanced Configuration\\n")
            f.write("# Updated via Web Interface\\n\\n")
            
            # Group related settings
            f.write("# Display Configuration\\n")
            for key in ['DISPLAY_WIDTH', 'DISPLAY_HEIGHT', 'DISPLAY_TYPE', 'VCOM_VALUE']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Bible API Configuration\\n")
            for key in ['BIBLE_API_URL', 'BIBLE_VERSION', 'FALLBACK_ENABLED']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Timing Configuration\\n")
            for key in ['UPDATE_INTERVAL', 'STARTUP_DELAY', 'RETRY_ATTEMPTS']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Logging Configuration\\n")
            for key in ['LOG_LEVEL', 'LOG_FILE', 'DEBUG_MODE']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Service Configuration\\n")
            for key in ['SERVICE_USER', 'WORKING_DIRECTORY']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Hardware Configuration\\n")
            for key in ['DRIVER_PATH', 'VCOM_CONFIG_FILE']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Performance Configuration\\n")
            for key in ['MEMORY_LIMIT_MB', 'REFRESH_OPTIMIZATION', 'FULL_REFRESH_INTERVAL']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Font Configuration\\n")
            for key in ['FONT_PATH', 'DEFAULT_FONT_SIZE', 'TITLE_FONT_SIZE', 'FONT_FAMILY']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Background Configuration\\n")
            for key in ['BACKGROUND_TYPE', 'BACKGROUND_COLOR', 'BACKGROUND_IMAGE', 'BACKGROUND_OPACITY']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
            
            f.write("\\n# Simulation Mode\\n")
            for key in ['SIMULATION_MODE']:
                if key in existing_config:
                    f.write(f"{key}={existing_config[key]}\\n")
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/validate', methods=['POST'])
def validate_config():
    """Validate Bible Clock configuration"""
    try:
        # Run the validation script
        import subprocess
        result = subprocess.run(
            ['python', 'bin/validate_config.py'],
            cwd=BIBLE_CLOCK_PATH,
            capture_output=True,
            text=True
        )
        
        return jsonify({
            'valid': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

