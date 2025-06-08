"""
Display handling module for the Bible Clock.
Supports both e-ink displays (Raspberry Pi) and PIL simulation.
Enhanced with new layout and side-by-side version display.
"""

import os
import tempfile
import subprocess
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import config
from amplified_bible import get_amplified_verse, has_amplified_verse


class DisplayManager:
    """Handles display output for both e-ink and simulation modes."""
    
    def __init__(self, simulate: bool = None):
        """
        Initialize the display manager.
        
        Args:
            simulate: Force simulation mode. Uses config.SIMULATE if None.
        """
        self.simulate = simulate if simulate is not None else config.SIMULATE
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        
        # Load fonts with larger sizes
        self.font = self._load_font(config.FONT_SIZE)  # Main text: 48
        self.title_font = self._load_font(config.FONT_SIZE + 8)  # Title: 56
        self.reference_font = self._load_font(config.FONT_SIZE - 4)  # Reference: 44
        self.small_font = self._load_font(config.FONT_SIZE - 16)  # Small text: 32
        
        if not self.simulate:
            self._init_eink()
        else:
            if config.DEBUG:
                print("Display manager in simulation mode")
    
    def _load_font(self, size: int) -> ImageFont.ImageFont:
        """Load a font with the specified size."""
        try:
            return ImageFont.truetype(config.DEFAULT_FONT_PATH, size)
        except (OSError, IOError):
            if config.DEBUG:
                print("Warning: Could not load custom font: unknown file format")
            return ImageFont.load_default()
    
    def _init_eink(self):
        """Initialize e-ink display (Raspberry Pi only)."""
        try:
            # This would import the specific e-ink library
            # For example, for Waveshare displays:
            # from waveshare_epd import epd7in5_V2
            # self.epd = epd7in5_V2.EPD()
            # self.epd.init()
            if config.DEBUG:
                print("E-ink display initialized")
        except ImportError:
            print("Warning: E-ink display library not available. Using simulation mode.")
            self.simulate = True
        except Exception as e:
            print(f"Warning: E-ink display initialization failed: {e}. Using simulation mode.")
            self.simulate = True
    
    def create_verse_image(self, book: str, verse_ref: str, verse_text: str, 
                          current_time: str, mode: str = config.CLOCK_MODE, 
                          version: str = config.KJV_ONLY) -> Image.Image:
        """
        Create an image with the verse and reference.
        
        Args:
            book: Bible book name
            verse_ref: Full verse reference (e.g., "John 3:16")
            verse_text: KJV verse text
            current_time: Current time string
            mode: Display mode (clock or day)
            version: Version display mode (kjv_only or kjv_amplified)
            
        Returns:
            PIL Image object
        """
        # Create image with white background
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        if version == config.KJV_AMPLIFIED:
            return self._create_side_by_side_image(draw, image, book, verse_ref, 
                                                 verse_text, current_time, mode)
        else:
            return self._create_single_version_image(draw, image, book, verse_ref, 
                                                   verse_text, current_time, mode)
    
    def _create_single_version_image(self, draw: ImageDraw.Draw, image: Image.Image,
                                   book: str, verse_ref: str, verse_text: str, 
                                   current_time: str, mode: str) -> Image.Image:
        """Create image with single version (KJV only) - new layout."""
        
        # Clean the verse text
        clean_text = self._clean_verse_text(verse_text)
        
        # Calculate text areas
        margin = config.VERSE_TEXT_MARGIN
        text_width = self.width - (2 * margin)
        
        # Wrap the verse text for center display
        wrapped_lines = self._wrap_text(clean_text, self.font, text_width)
        
        # Calculate vertical positioning for centered text
        line_height = self.font.getbbox("Ay")[3] - self.font.getbbox("Ay")[1] + 10
        total_text_height = len(wrapped_lines) * line_height
        start_y = (self.height - total_text_height) // 2
        
        # Draw the verse text in the center
        current_y = start_y
        for line in wrapped_lines:
            # Center each line horizontally
            line_bbox = draw.textbbox((0, 0), line, font=self.font)
            line_width = line_bbox[2] - line_bbox[0]
            x = (self.width - line_width) // 2
            
            draw.text((x, current_y), line, font=self.font, fill='black')
            current_y += line_height
        
        # Draw reference in bottom right
        ref_margin = config.REFERENCE_MARGIN
        ref_bbox = draw.textbbox((0, 0), verse_ref, font=self.reference_font)
        ref_width = ref_bbox[2] - ref_bbox[0]
        ref_height = ref_bbox[3] - ref_bbox[1]
        
        ref_x = self.width - ref_width - ref_margin
        ref_y = self.height - ref_height - ref_margin
        
        draw.text((ref_x, ref_y), verse_ref, font=self.reference_font, fill='black')
        
        # Add mode indicator in top left (small)
        mode_text = f"Mode: {mode.title()}"
        if mode == config.DAY_MODE:
            from datetime import date
            today = date.today()
            mode_text += f" ({today.strftime('%B %d')})"
        
        draw.text((20, 20), mode_text, font=self.small_font, fill='gray')
        
        return image
    
    def _create_side_by_side_image(self, draw: ImageDraw.Draw, image: Image.Image,
                                 book: str, verse_ref: str, kjv_text: str, 
                                 current_time: str, mode: str) -> Image.Image:
        """Create image with KJV and Amplified side by side."""
        
        # Get Amplified verse
        try:
            # Parse verse reference to get chapter and verse numbers
            parts = verse_ref.split()
            if len(parts) >= 2:
                chapter_verse = parts[-1]  # Get "3:16" part
                chapter, verse = map(int, chapter_verse.split(':'))
                amplified_text = get_amplified_verse(book, chapter, verse)
            else:
                amplified_text = None
        except:
            amplified_text = None
        
        if not amplified_text:
            # Fallback to single version if Amplified not available
            return self._create_single_version_image(draw, image, book, verse_ref, 
                                                   kjv_text, current_time, mode)
        
        # Clean both texts
        clean_kjv = self._clean_verse_text(kjv_text)
        clean_amplified = self._clean_verse_text(amplified_text)
        
        # Calculate layout for side-by-side
        margin = config.SIDE_BY_SIDE_MARGIN
        divider_x = self.width // 2
        left_width = divider_x - (2 * margin)
        right_width = self.width - divider_x - (2 * margin)
        
        # Wrap text for both versions
        kjv_lines = self._wrap_text(clean_kjv, self.font, left_width)
        amp_lines = self._wrap_text(clean_amplified, self.font, right_width)
        
        # Calculate starting positions
        line_height = self.font.getbbox("Ay")[3] - self.font.getbbox("Ay")[1] + 8
        header_height = 60
        start_y = header_height
        
        # Draw headers
        draw.text((margin, 20), "KJV", font=self.title_font, fill='black')
        draw.text((divider_x + margin, 20), "Amplified", font=self.title_font, fill='black')
        
        # Draw divider line
        draw.line([(divider_x, header_height), (divider_x, self.height - 80)], 
                 fill='lightgray', width=2)
        
        # Draw KJV text (left side)
        current_y = start_y
        for line in kjv_lines:
            if current_y + line_height > self.height - 100:  # Leave space for reference
                break
            draw.text((margin, current_y), line, font=self.font, fill='black')
            current_y += line_height
        
        # Draw Amplified text (right side)
        current_y = start_y
        for line in amp_lines:
            if current_y + line_height > self.height - 100:  # Leave space for reference
                break
            draw.text((divider_x + margin, current_y), line, font=self.font, fill='black')
            current_y += line_height
        
        # Draw reference in bottom center
        ref_bbox = draw.textbbox((0, 0), verse_ref, font=self.reference_font)
        ref_width = ref_bbox[2] - ref_bbox[0]
        ref_height = ref_bbox[3] - ref_bbox[1]
        
        ref_x = (self.width - ref_width) // 2
        ref_y = self.height - ref_height - config.REFERENCE_MARGIN
        
        draw.text((ref_x, ref_y), verse_ref, font=self.reference_font, fill='black')
        
        # Add mode indicator
        mode_text = f"Mode: {mode.title()}"
        if mode == config.DAY_MODE:
            from datetime import date
            today = date.today()
            mode_text += f" ({today.strftime('%B %d')})"
        
        draw.text((20, self.height - 40), mode_text, font=self.small_font, fill='gray')
        
        return image
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int) -> list:
        """Wrap text to fit within the specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed the width
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text by removing formatting markers."""
        # Remove common formatting markers
        text = text.replace('[', '').replace(']', '')
        text = text.replace('#', '')
        text = text.replace('*', '')
        
        # Clean up extra spaces
        text = ' '.join(text.split())
        
        return text
    
    def display_verse(self, book: str, verse_ref: str, verse_text: str, 
                     current_time: str, mode: str = config.CLOCK_MODE,
                     version: str = config.KJV_ONLY) -> Optional[str]:
        """
        Display a verse on the screen.
        
        Args:
            book: Bible book name
            verse_ref: Full verse reference
            verse_text: Verse text
            current_time: Current time string
            mode: Display mode
            version: Version display mode
            
        Returns:
            Path to saved image (simulation mode) or None
        """
        image = self.create_verse_image(book, verse_ref, verse_text, current_time, mode, version)
        
        if self.simulate:
            # Save to temporary file and display
            temp_path = os.path.join(os.path.dirname(__file__), '..', 'temp_display.png')
            image.save(temp_path)
            
            if config.DEBUG:
                print(f"Display image saved to: {temp_path}")
                print(f"Time: {current_time}")
                print(f"Verse: {verse_ref}")
                print(f"Text: {verse_text[:80]}...")
                print(f"Mode: {mode}")
                print(f"Version: {version}")
            
            # Try to open the image (optional)
            try:
                # Create a temporary copy for viewing
                with tempfile.NamedTemporaryFile(suffix='.PNG', delete=False) as tmp:
                    image.save(tmp.name)
                    subprocess.run(['xdg-open', tmp.name], check=False, 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass  # Ignore errors in opening the image
            
            return temp_path
        else:
            # Display on e-ink screen
            try:
                # Convert to 1-bit for e-ink display
                bw_image = image.convert('1')
                # self.epd.display(self.epd.getbuffer(bw_image))
                if config.DEBUG:
                    print("Image displayed on e-ink screen")
            except Exception as e:
                print(f"Error displaying on e-ink: {e}")
            
            return None
    
    def clear_display(self):
        """Clear the display."""
        if not self.simulate:
            try:
                # self.epd.Clear()
                if config.DEBUG:
                    print("E-ink display cleared")
            except Exception as e:
                print(f"Error clearing e-ink display: {e}")
        else:
            if config.DEBUG:
                print("Display cleared (simulation)")
    
    def sleep_display(self):
        """Put the display to sleep (e-ink only)."""
        if not self.simulate:
            try:
                # self.epd.sleep()
                if config.DEBUG:
                    print("E-ink display sleeping")
            except Exception as e:
                print(f"Error putting e-ink display to sleep: {e}")
        else:
            if config.DEBUG:
                print("Display sleep (simulation)")
    
    def get_display_info(self) -> dict:
        """
        Get information about the display configuration.
        
        Returns:
            Dictionary with display information
        """
        return {
            'width': self.width,
            'height': self.height,
            'simulate': self.simulate,
            'font_size': config.FONT_SIZE
        }

