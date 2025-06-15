from flask import Blueprint, jsonify, send_file
import os
import glob
from pathlib import Path

backgrounds_bp = Blueprint('backgrounds', __name__)

# Path to backgrounds
BACKGROUNDS_PATH = '/home/ubuntu/bible-clock-enhanced/data/backgrounds'

@backgrounds_bp.route('/backgrounds', methods=['GET'])
def get_backgrounds():
    """Get list of available background options"""
    try:
        backgrounds = [
            {
                'id': 'solid',
                'name': 'Solid Color',
                'description': 'Clean white background for maximum readability',
                'preview_url': None,
                'type': 'solid'
            },
            {
                'id': 'subtle_cross',
                'name': 'Subtle Cross',
                'description': 'Delicate cross pattern watermark',
                'preview_url': '/api/backgrounds/preview/subtle_cross.png',
                'type': 'pattern'
            },
            {
                'id': 'scripture_border',
                'name': 'Scripture Border',
                'description': 'Elegant decorative border with biblical motifs',
                'preview_url': '/api/backgrounds/preview/scripture_border.png',
                'type': 'border'
            },
            {
                'id': 'dove_watermark',
                'name': 'Dove Watermark',
                'description': 'Graceful dove silhouette representing the Holy Spirit',
                'preview_url': '/api/backgrounds/preview/dove_watermark.png',
                'type': 'watermark'
            },
            {
                'id': 'vine_pattern',
                'name': 'Vine Pattern',
                'description': 'Flowing vine branches symbolizing connection to Christ',
                'preview_url': '/api/backgrounds/preview/vine_pattern.png',
                'type': 'pattern'
            },
            {
                'id': 'geometric_light',
                'name': 'Light Geometric',
                'description': 'Modern geometric pattern with clean lines',
                'preview_url': '/api/backgrounds/preview/geometric_light.png',
                'type': 'pattern'
            },
            {
                'id': 'parchment',
                'name': 'Parchment Texture',
                'description': 'Subtle aged paper texture evoking ancient manuscripts',
                'preview_url': '/api/backgrounds/preview/parchment.png',
                'type': 'texture'
            },
            {
                'id': 'minimalist_frame',
                'name': 'Minimalist Frame',
                'description': 'Simple rectangular border for structured presentation',
                'preview_url': '/api/backgrounds/preview/minimalist_frame.png',
                'type': 'border'
            }
        ]
        
        return jsonify(backgrounds)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backgrounds_bp.route('/backgrounds/preview/<filename>')
def get_background_preview(filename):
    """Get background preview image"""
    try:
        file_path = os.path.join(BACKGROUNDS_PATH, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        else:
            return jsonify({'error': 'Background not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@backgrounds_bp.route('/backgrounds/apply/<background_id>', methods=['POST'])
def apply_background(background_id):
    """Apply a background to the Bible Clock"""
    try:
        # Update the configuration file
        config_file = '/home/ubuntu/bible-clock-enhanced/.env'
        
        # Read existing config
        config_lines = []
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_lines = f.readlines()
        
        # Update background settings
        updated = False
        for i, line in enumerate(config_lines):
            if line.startswith('BACKGROUND_TYPE='):
                config_lines[i] = f'BACKGROUND_TYPE={background_id}\\n'
                updated = True
                break
        
        if not updated:
            config_lines.append(f'BACKGROUND_TYPE={background_id}\\n')
        
        # Write back to file
        with open(config_file, 'w') as f:
            f.writelines(config_lines)
        
        return jsonify({
            'success': True,
            'message': f'Background "{background_id}" applied successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

