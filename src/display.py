"""
Enhanced Display handling module for the Bible Clock with temporary mode display.
Supports both e-ink displays (Raspberry Pi) and PIL simulation.
Enhanced with temporary mode indicator that disappears after a few seconds.
"""

import os
import tempfile
import subprocess
import time
import threading
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import config
try:
    from amplified_bible import get_amplified_verse, has_amplified_verse
except ImportError:
    # Fallback if amplified_bible module doesn't exist
    def get_amplified_verse(book, chapter, verse):
        return None
    def has_amplified_verse(book, chapter, verse):
        return False


class DisplayManager:
    """Handles display output with temporary mode indicator functionality."""
    
    def __init__(self, simulate: bool = None):
        """
        Initialize the display manager.
        
        Args:
            simulate: Force simulation mode. Uses config.SIMULATE if None.
        """
        self.simulate = simulate if simulate is not None else config.SIMULATE
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        
        # Base font sizes (will be dynamically adjusted)
        self.base_font_size = config.FONT_SIZE
        self.base_title_font_size = config.FONT_SIZE + 8
        self.base_reference_font_size = config.FONT_SIZE - 4
        self.base_small_font_size = config.FONT_SIZE - 16
        
        # Minimum font sizes to maintain readability
        self.min_font_size = 20
        self.min_title_font_size = 24
        self.min_reference_font_size = 18
        self.min_small_font_size = 14
        
        # Temporary mode display settings
        self.show_mode_indicator = False
        self.mode_indicator_timer = None
        self.mode_display_duration = 3.0  # Show mode for 3 seconds
        self.last_mode_change_time = 0
        
        if not self.simulate:
            self._init_eink()
        else:
            if config.DEBUG:
                print("Display manager in simulation mode with temporary mode display")
    
    def trigger_mode_display(self, mode: str):
        """
        Trigger temporary mode display for a few seconds.
        
        Args:
            mode: Current mode to display
        """
        self.show_mode_indicator = True
        self.last_mode_change_time = time.time()
        
        # Cancel existing timer if any
        if self.mode_indicator_timer:
            self.mode_indicator_timer.cancel()
        
        # Set timer to hide mode indicator
        self.mode_indicator_timer = threading.Timer(
            self.mode_display_duration, 
            self._hide_mode_indicator
        )
        self.mode_indicator_timer.start()
        
        if config.DEBUG:
            print(f"Mode indicator triggered: {mode} (will hide in {self.mode_display_duration}s)")
    
    def _hide_mode_indicator(self):
        """Hide the mode indicator after timer expires."""
        self.show_mode_indicator = False
        if config.DEBUG:
            print("Mode indicator hidden")
    
    def should_show_mode_indicator(self) -> bool:
        """
        Check if mode indicator should be shown.
        
        Returns:
            True if mode indicator should be displayed
        """
        return self.show_mode_indicator
    
    def _load_font(self, size: int) -> ImageFont.ImageFont:
        """Load a font with the specified size."""
        try:
            return ImageFont.truetype(config.DEFAULT_FONT_PATH, size)
        except (OSError, IOError):
            if config.DEBUG:
                print("Warning: Could not load custom font: unknown file format")
            return ImageFont.load_default()
    
    def _calculate_optimal_font_size(self, text: str, max_width: int, max_height: int, 
                                   base_font_size: int, min_font_size: int) -> Tuple[ImageFont.ImageFont, int]:
        """
        Calculate the optimal font size to fit text within given dimensions.
        
        Args:
            text: Text to fit
            max_width: Maximum width available
            max_height: Maximum height available
            base_font_size: Starting font size
            min_font_size: Minimum acceptable font size
            
        Returns:
            Tuple of (font object, actual font size used)
        """
        current_size = base_font_size
        
        while current_size >= min_font_size:
            font = self._load_font(current_size)
            wrapped_lines = self._wrap_text(text, font, max_width)
            
            # Calculate total height needed
            line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 10
            total_height = len(wrapped_lines) * line_height
            
            # Check if it fits
            if total_height <= max_height:
                if config.DEBUG and current_size != base_font_size:
                    print(f"Auto-resized font from {base_font_size} to {current_size} for better fit")
                return font, current_size
            
            # Reduce font size and try again
            current_size -= 2
        
        # Use minimum size if nothing else works
        if config.DEBUG:
            print(f"Using minimum font size {min_font_size} - content may be truncated")
        return self._load_font(min_font_size), min_font_size
    
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
                          current_time: str, mode: str = "clock", 
                          version: str = "kjv_only", description: str = "") -> Image.Image:
        """
        Create an image with the verse and reference, with optional temporary mode display.
        
        Args:
            book: Bible book name
            verse_ref: Full verse reference (e.g., "John 3:16")
            verse_text: KJV verse text
            current_time: Current time string
            mode: Display mode (clock, day, or expand)
            version: Version display mode (kjv_only or kjv_amplified)
            description: Additional description for expand mode
            
        Returns:
            PIL Image object
        """
        # Create image with white background
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        
        if version == "kjv_amplified":
            return self._create_side_by_side_image_auto_resize(draw, image, book, verse_ref, 
                                                             verse_text, current_time, mode, description)
        else:
            return self._create_single_version_image_auto_resize(draw, image, book, verse_ref, 
                                                               verse_text, current_time, mode, description)
    
    def _create_single_version_image_auto_resize(self, draw: ImageDraw.Draw, image: Image.Image,
                                               book: str, verse_ref: str, verse_text: str, 
                                               current_time: str, mode: str, description: str = "") -> Image.Image:
        """Create image with single version (KJV only) with automatic text resizing and temporary mode display."""
        
        # Clean the verse text
        clean_text = self._clean_verse_text(verse_text)
        
        # Calculate available space for text
        margin = getattr(config, 'VERSE_TEXT_MARGIN', 80)
        text_width = self.width - (2 * margin)
        
        # Reserve space for reference and mode indicator (if shown)
        reference_space = 80  # Space for reference at bottom
        mode_space = 50 if self.should_show_mode_indicator() else 20  # Space for mode indicator at top
        available_height = self.height - reference_space - mode_space
        
        # Calculate optimal font size for the main text
        font, actual_font_size = self._calculate_optimal_font_size(
            clean_text, text_width, available_height, 
            self.base_font_size, self.min_font_size
        )
        
        # Calculate proportional sizes for other text elements
        size_ratio = actual_font_size / self.base_font_size
        title_size = max(int(self.base_title_font_size * size_ratio), self.min_title_font_size)
        reference_size = max(int(self.base_reference_font_size * size_ratio), self.min_reference_font_size)
        small_size = max(int(self.base_small_font_size * size_ratio), self.min_small_font_size)
        
        title_font = self._load_font(title_size)
        reference_font = self._load_font(reference_size)
        small_font = self._load_font(small_size)
        
        # Wrap the verse text
        wrapped_lines = self._wrap_text(clean_text, font, text_width)
        
        # Calculate vertical positioning for centered text
        line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 10
        total_text_height = len(wrapped_lines) * line_height
        start_y = mode_space + (available_height - total_text_height) // 2
        
        # Draw the verse text in the center
        current_y = start_y
        for line in wrapped_lines:
            # Center each line horizontally
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            x = (self.width - line_width) // 2
            
            draw.text((x, current_y), line, font=font, fill='black')
            current_y += line_height
        
        # Draw reference in bottom right
        ref_margin = getattr(config, 'REFERENCE_MARGIN', 50)
        ref_bbox = draw.textbbox((0, 0), verse_ref, font=reference_font)
        ref_width = ref_bbox[2] - ref_bbox[0]
        ref_height = ref_bbox[3] - ref_bbox[1]
        
        ref_x = self.width - ref_width - ref_margin
        ref_y = self.height - ref_height - ref_margin
        
        draw.text((ref_x, ref_y), verse_ref, font=reference_font, fill='black')
        
        # Add temporary mode indicator in top left (only if should be shown)
        if self.should_show_mode_indicator():
            if mode == "expand" and description:
                mode_text = description
            else:
                mode_text = f"Mode: {mode.title()}"
                if mode == "day":
                    from datetime import date
                    today = date.today()
                    mode_text += f" ({today.strftime('%B %d')})"
            
            # Draw mode indicator with background for visibility
            mode_bbox = draw.textbbox((0, 0), mode_text, font=small_font)
            mode_width = mode_bbox[2] - mode_bbox[0]
            mode_height = mode_bbox[3] - mode_bbox[1]
            
            # Draw background rectangle
            padding = 10
            draw.rectangle([
                (15, 15), 
                (25 + mode_width + padding, 25 + mode_height + padding)
            ], fill='lightgray', outline='gray')
            
            draw.text((20, 20), mode_text, font=small_font, fill='black')
        
        # Add font size indicator for debugging (optional)
        if config.DEBUG and actual_font_size != self.base_font_size:
            debug_text = f"Font: {actual_font_size}px (auto-resized from {self.base_font_size}px)"
            draw.text((20, self.height - 20), debug_text, font=small_font, fill='lightgray')
        
        return image
    
    def _create_side_by_side_image_auto_resize(self, draw: ImageDraw.Draw, image: Image.Image,
                                             book: str, verse_ref: str, kjv_text: str, 
                                             current_time: str, mode: str, description: str = "") -> Image.Image:
        """Create image with KJV and Amplified side by side with automatic resizing and temporary mode display."""
        
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
            return self._create_single_version_image_auto_resize(draw, image, book, verse_ref, 
                                                               kjv_text, current_time, mode)
        
        # Clean both texts
        clean_kjv = self._clean_verse_text(kjv_text)
        clean_amplified = self._clean_verse_text(amplified_text)
        
        # Calculate layout for side-by-side
        margin = getattr(config, 'SIDE_BY_SIDE_MARGIN', 20)
        divider_x = self.width // 2
        left_width = divider_x - (2 * margin)
        right_width = self.width - divider_x - (2 * margin)
        
        # Calculate available height
        header_height = 60
        footer_height = 100
        available_height = self.height - header_height - footer_height
        
        # Find optimal font size for both texts
        kjv_font, kjv_size = self._calculate_optimal_font_size(
            clean_kjv, left_width, available_height,
            self.base_font_size, self.min_font_size
        )
        
        amp_font, amp_size = self._calculate_optimal_font_size(
            clean_amplified, right_width, available_height,
            self.base_font_size, self.min_font_size
        )
        
        # Use the smaller font size for consistency
        final_size = min(kjv_size, amp_size)
        font = self._load_font(final_size)
        
        # Calculate proportional sizes for other elements
        size_ratio = final_size / self.base_font_size
        title_size = max(int(self.base_title_font_size * size_ratio), self.min_title_font_size)
        reference_size = max(int(self.base_reference_font_size * size_ratio), self.min_reference_font_size)
        small_size = max(int(self.base_small_font_size * size_ratio), self.min_small_font_size)
        
        title_font = self._load_font(title_size)
        reference_font = self._load_font(reference_size)
        small_font = self._load_font(small_size)
        
        # Wrap text for both versions
        kjv_lines = self._wrap_text(clean_kjv, font, left_width)
        amp_lines = self._wrap_text(clean_amplified, font, right_width)
        
        # Calculate starting positions
        line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1] + 8
        start_y = header_height
        
        # Draw headers
        draw.text((margin, 20), "KJV", font=title_font, fill='black')
        draw.text((divider_x + margin, 20), "Amplified", font=title_font, fill='black')
        
        # Draw divider line
        draw.line([(divider_x, header_height), (divider_x, self.height - footer_height)], 
                 fill='lightgray', width=2)
        
        # Draw KJV text (left side)
        current_y = start_y
        for line in kjv_lines:
            if current_y + line_height > self.height - footer_height:
                break
            draw.text((margin, current_y), line, font=font, fill='black')
            current_y += line_height
        
        # Draw Amplified text (right side)
        current_y = start_y
        for line in amp_lines:
            if current_y + line_height > self.height - footer_height:
                break
            draw.text((divider_x + margin, current_y), line, font=font, fill='black')
            current_y += line_height
        
        # Draw reference in bottom center
        ref_bbox = draw.textbbox((0, 0), verse_ref, font=reference_font)
        ref_width = ref_bbox[2] - ref_bbox[0]
        ref_height = ref_bbox[3] - ref_bbox[1]
        
        ref_x = (self.width - ref_width) // 2
        ref_y = self.height - ref_height - getattr(config, 'REFERENCE_MARGIN', 50)
        
        draw.text((ref_x, ref_y), verse_ref, font=reference_font, fill='black')
        
        # Add temporary mode indicator (only if should be shown)
        if self.should_show_mode_indicator():
            mode_text = f"Mode: {mode.title()}"
            if mode == "day":
                from datetime import date
                today = date.today()
                mode_text += f" ({today.strftime('%B %d')})"
            
            # Draw mode indicator with background
            mode_bbox = draw.textbbox((0, 0), mode_text, font=small_font)
            mode_width = mode_bbox[2] - mode_bbox[0]
            mode_height = mode_bbox[3] - mode_bbox[1]
            
            # Position in bottom left
            padding = 8
            draw.rectangle([
                (15, self.height - 45), 
                (25 + mode_width + padding, self.height - 25)
            ], fill='lightgray', outline='gray')
            
            draw.text((20, self.height - 40), mode_text, font=small_font, fill='black')
        
        # Add font size indicator for debugging
        if config.DEBUG and final_size != self.base_font_size:
            debug_text = f"Font: {final_size}px (auto-resized)"
            draw.text((self.width - 200, self.height - 20), debug_text, font=small_font, fill='lightgray')
        
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
                     current_time: str, mode: str = "clock",
                     version: str = "kjv_only") -> Optional[str]:
        """
        Display a verse on the screen with automatic text resizing and temporary mode display.
        
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
                print(f"Mode indicator shown: {self.should_show_mode_indicator()}")
            
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
    
    def cleanup(self):
        """Clean up resources including timers."""
        if self.mode_indicator_timer:
            self.mode_indicator_timer.cancel()
    
    def get_display_info(self) -> dict:
        """
        Get display information and current settings.
        
        Returns:
            Dictionary with display information
        """
        return {
            'width': self.width,
            'height': self.height,
            'simulate': self.simulate,
            'base_font_size': self.base_font_size,
            'min_font_size': self.min_font_size,
            'auto_resize_enabled': True,
            'temporary_mode_display': True,
            'mode_display_duration': self.mode_display_duration,
            'show_mode_indicator': self.show_mode_indicator
        }

