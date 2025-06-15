"""
Enhanced Image Generator

This module handles image generation for the e-ink display with optimized
layouts, font management, and performance optimizations.
"""

import logging
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import textwrap
import os

class ImageGenerator:
    """Enhanced image generator for e-ink display"""
    
    def __init__(self, width: int = 1872, height: int = 1404, font_path: str = "data/fonts"):
        self.width = width
        self.height = height
        self.font_path = Path(font_path)
        self.logger = logging.getLogger(__name__)
        
        # Font cache for performance
        self.font_cache = {}
        
        # Layout configuration
        self.margins = {
            'top': 80,
            'bottom': 80,
            'left': 100,
            'right': 100
        }
        
        # Color configuration for e-ink
        self.colors = {
            'background': 255,  # White
            'text': 0,          # Black
            'accent': 128       # Gray (for e-ink displays that support it)
        }
        
        # Load default fonts
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Load default fonts with fallbacks"""
        # Try to load custom fonts first
        font_files = {
            'title': ['DejaVuSans-Bold.ttf', 'arial.ttf', 'helvetica.ttf'],
            'verse': ['DejaVuSans.ttf', 'arial.ttf', 'helvetica.ttf'],
            'reference': ['DejaVuSans-Bold.ttf', 'arial.ttf', 'helvetica.ttf'],
            'time': ['DejaVuSans-Bold.ttf', 'arial.ttf', 'helvetica.ttf']
        }
        
        for font_type, font_names in font_files.items():
            font_loaded = False
            
            for font_name in font_names:
                font_file = self.font_path / font_name
                if font_file.exists():
                    try:
                        # Load different sizes
                        self.font_cache[f'{font_type}_large'] = ImageFont.truetype(str(font_file), 48)
                        self.font_cache[f'{font_type}_medium'] = ImageFont.truetype(str(font_file), 36)
                        self.font_cache[f'{font_type}_small'] = ImageFont.truetype(str(font_file), 24)
                        font_loaded = True
                        self.logger.info(f"Loaded font {font_name} for {font_type}")
                        break
                    except Exception as e:
                        self.logger.warning(f"Failed to load font {font_name}: {e}")
            
            if not font_loaded:
                # Use default font as fallback
                try:
                    self.font_cache[f'{font_type}_large'] = ImageFont.load_default()
                    self.font_cache[f'{font_type}_medium'] = ImageFont.load_default()
                    self.font_cache[f'{font_type}_small'] = ImageFont.load_default()
                    self.logger.warning(f"Using default font for {font_type}")
                except Exception as e:
                    self.logger.error(f"Failed to load default font for {font_type}: {e}")
    
    def generate_verse_image(self, verse_data: Dict[str, str]) -> Image.Image:
        """
        Generate image for verse display
        
        Args:
            verse_data: Formatted verse data with components
            
        Returns:
            PIL Image ready for display
        """
        # Create image with white background (255 = white for e-ink)
        image = Image.new('L', (self.width, self.height), 255)  # 'L' mode for grayscale
        draw = ImageDraw.Draw(image)
        
        # Calculate layout areas
        layout = self._calculate_layout()
        
        # Draw components
        current_y = layout['content_top']
        
        # Draw time and date
        current_y = self._draw_time_section(draw, verse_data, layout, current_y)
        
        # Add spacing
        current_y += 40
        
        # Draw verse reference
        current_y = self._draw_reference(draw, verse_data, layout, current_y)
        
        # Add spacing
        current_y += 30
        
        # Draw verse text
        current_y = self._draw_verse_text(draw, verse_data, layout, current_y)
        
        # Draw footer (translation, source info)
        self._draw_footer(draw, verse_data, layout)
        
        # Add decorative elements if space allows
        self._add_decorative_elements(draw, layout)
        
        return image
    
    def _calculate_layout(self) -> Dict[str, int]:
        """Calculate layout dimensions"""
        return {
            'content_left': self.margins['left'],
            'content_right': self.width - self.margins['right'],
            'content_top': self.margins['top'],
            'content_bottom': self.height - self.margins['bottom'],
            'content_width': self.width - self.margins['left'] - self.margins['right'],
            'content_height': self.height - self.margins['top'] - self.margins['bottom']
        }
    
    def _draw_time_section(self, draw: ImageDraw.Draw, verse_data: Dict[str, str], 
                          layout: Dict[str, int], start_y: int) -> int:
        """Draw time and date section"""
        time_text = verse_data.get('time', '')
        date_text = verse_data.get('date', '')
        
        if time_text:
            # Draw time (large)
            font = self.font_cache.get('time_large', ImageFont.load_default())
            time_bbox = draw.textbbox((0, 0), time_text, font=font)
            time_width = time_bbox[2] - time_bbox[0]
            time_height = time_bbox[3] - time_bbox[1]
            
            time_x = layout['content_left'] + (layout['content_width'] - time_width) // 2
            draw.text((time_x, start_y), time_text, font=font, fill=self.colors['text'])
            
            current_y = start_y + time_height + 10
            
            # Draw date (smaller)
            if date_text:
                font = self.font_cache.get('time_small', ImageFont.load_default())
                date_bbox = draw.textbbox((0, 0), date_text, font=font)
                date_width = date_bbox[2] - date_bbox[0]
                date_height = date_bbox[3] - date_bbox[1]
                
                date_x = layout['content_left'] + (layout['content_width'] - date_width) // 2
                draw.text((date_x, current_y), date_text, font=font, fill=self.colors['text'])
                
                current_y += date_height
            
            return current_y
        
        return start_y
    
    def _draw_reference(self, draw: ImageDraw.Draw, verse_data: Dict[str, str], 
                       layout: Dict[str, int], start_y: int) -> int:
        """Draw verse reference"""
        reference = verse_data.get('reference', '')
        
        if reference:
            font = self.font_cache.get('reference_medium', ImageFont.load_default())
            ref_bbox = draw.textbbox((0, 0), reference, font=font)
            ref_width = ref_bbox[2] - ref_bbox[0]
            ref_height = ref_bbox[3] - ref_bbox[1]
            
            ref_x = layout['content_left'] + (layout['content_width'] - ref_width) // 2
            draw.text((ref_x, start_y), reference, font=font, fill=self.colors['text'])
            
            return start_y + ref_height
        
        return start_y
    
    def _draw_verse_text(self, draw: ImageDraw.Draw, verse_data: Dict[str, str], 
                        layout: Dict[str, int], start_y: int) -> int:
        """Draw verse text with word wrapping"""
        text = verse_data.get('text', '')
        
        if not text:
            return start_y
        
        font = self.font_cache.get('verse_medium', ImageFont.load_default())
        
        # Calculate available space
        available_width = layout['content_width']
        available_height = layout['content_bottom'] - start_y - 100  # Reserve space for footer
        
        # Wrap text
        wrapped_lines = self._wrap_text(text, font, available_width)
        
        # Calculate line height
        line_bbox = draw.textbbox((0, 0), "Ay", font=font)
        line_height = line_bbox[3] - line_bbox[1] + 8  # Add line spacing
        
        # Check if text fits
        total_text_height = len(wrapped_lines) * line_height
        
        if total_text_height > available_height:
            # Try smaller font
            font = self.font_cache.get('verse_small', ImageFont.load_default())
            wrapped_lines = self._wrap_text(text, font, available_width)
            line_bbox = draw.textbbox((0, 0), "Ay", font=font)
            line_height = line_bbox[3] - line_bbox[1] + 6
            total_text_height = len(wrapped_lines) * line_height
        
        # Center text vertically in available space
        text_start_y = start_y + (available_height - total_text_height) // 2
        
        # Draw each line
        current_y = text_start_y
        for line in wrapped_lines:
            if current_y + line_height > layout['content_bottom'] - 50:
                break  # Don't overflow into footer area
            
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = layout['content_left'] + (layout['content_width'] - line_width) // 2
            
            draw.text((line_x, current_y), line, font=font, fill=self.colors['text'])
            current_y += line_height
        
        return current_y
    
    def _draw_footer(self, draw: ImageDraw.Draw, verse_data: Dict[str, str], 
                    layout: Dict[str, int]):
        """Draw footer with translation and source info"""
        footer_y = layout['content_bottom'] - 40
        
        # Translation info
        translation = verse_data.get('translation', 'KJV')
        source = verse_data.get('source', '')
        
        footer_text = translation
        if source and source != 'api':
            footer_text += f" ({source})"
        
        if verse_data.get('is_special', False):
            footer_text += " ★"
        
        font = self.font_cache.get('reference_small', ImageFont.load_default())
        footer_bbox = draw.textbbox((0, 0), footer_text, font=font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        
        footer_x = layout['content_left'] + (layout['content_width'] - footer_width) // 2
        draw.text((footer_x, footer_y), footer_text, font=font, fill=self.colors['text'])
    
    def _add_decorative_elements(self, draw: ImageDraw.Draw, layout: Dict[str, int]):
        """Add subtle decorative elements"""
        # Simple border
        border_width = 2
        draw.rectangle([
            layout['content_left'] - border_width,
            layout['content_top'] - border_width,
            layout['content_right'] + border_width,
            layout['content_bottom'] + border_width
        ], outline=self.colors['text'], width=1)
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> list:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed width
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def generate_error_image(self, error_message: str = "Unable to load verse") -> Image.Image:
        """Generate error image when verse cannot be loaded"""
        image = Image.new('L', (self.width, self.height), 255)  # 'L' mode for grayscale
        draw = ImageDraw.Draw(image)
        
        layout = self._calculate_layout()
        
        # Draw error message
        font = self.font_cache.get('verse_medium', ImageFont.load_default())
        
        # Center the error message
        error_bbox = draw.textbbox((0, 0), error_message, font=font)
        error_width = error_bbox[2] - error_bbox[0]
        error_height = error_bbox[3] - error_bbox[1]
        
        error_x = layout['content_left'] + (layout['content_width'] - error_width) // 2
        error_y = layout['content_top'] + (layout['content_height'] - error_height) // 2
        
        draw.text((error_x, error_y), error_message, font=font, fill=self.colors['text'])
        
        return image
    
    def get_font_info(self) -> Dict[str, Any]:
        """Get information about loaded fonts"""
        return {
            'font_path': str(self.font_path),
            'loaded_fonts': list(self.font_cache.keys()),
            'font_cache_size': len(self.font_cache)
        }

