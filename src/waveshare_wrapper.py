"""
Enhanced Waveshare IT8951 Driver Wrapper

This module provides an optimized wrapper for the official Waveshare IT8951 driver
with performance optimizations, error handling, and memory management.
"""

import subprocess
import os
import tempfile
import hashlib
import logging
from PIL import Image
from typing import Optional, Tuple
from pathlib import Path

class WaveshareIT8951:
    """Enhanced Waveshare IT8951 driver wrapper with optimizations"""
    
    def __init__(self, vcom_value: str = "-1.50", driver_path: str = None):
        self.vcom_value = vcom_value
        self.driver_path = driver_path or "/home/pi/bible-clock-drivers/epd"
        self.width = 1872
        self.height = 1404
        self.logger = logging.getLogger(__name__)
        
        # Performance optimization attributes
        self.last_image_hash = None
        self.refresh_count = 0
        self.full_refresh_interval = 10
        
        # Validate driver availability
        if not Path(self.driver_path).exists():
            raise FileNotFoundError(f"Driver not found: {self.driver_path}")
        if not os.access(self.driver_path, os.X_OK):
            raise PermissionError(f"Driver not executable: {self.driver_path}")
    
    def init(self) -> bool:
        """Initialize the display"""
        try:
            self.logger.info("Initializing IT8951 display")
            result = subprocess.run(
                [self.driver_path, self.vcom_value, "0"], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Display initialized successfully with VCOM {self.vcom_value}")
                return True
            else:
                self.logger.error(f"Display initialization failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Display initialization timed out")
            return False
        except Exception as e:
            self.logger.error(f"Display initialization failed: {e}")
            return False
    
    def display(self, image: Image.Image, force_refresh: bool = False) -> bool:
        """
        Display an image on the e-ink screen with optimization
        
        Args:
            image: PIL Image to display
            force_refresh: Force full refresh regardless of optimization
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare image
            processed_image = self._prepare_image(image)
            
            # Check if image has changed (optimization)
            if not force_refresh and self._should_skip_refresh(processed_image):
                self.logger.debug("Skipping refresh - image unchanged")
                return True
            
            # Determine refresh type
            refresh_mode = self._get_refresh_mode(force_refresh)
            
            # Create temporary file for image
            with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as tmp_file:
                try:
                    # Save image as BMP
                    processed_image.save(tmp_file.name, 'BMP')
                    tmp_file.flush()
                    
                    # Call driver to display image
                    result = subprocess.run(
                        [self.driver_path, self.vcom_value, refresh_mode, tmp_file.name], 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    
                    if result.returncode == 0:
                        self._update_optimization_state(processed_image)
                        self.logger.debug(f"Display updated successfully (mode: {refresh_mode})")
                        return True
                    else:
                        self.logger.error(f"Display update failed: {result.stderr}")
                        return False
                        
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file.name)
                    except OSError:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Display update failed: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear the display"""
        try:
            self.logger.info("Clearing display")
            result = subprocess.run(
                [self.driver_path, self.vcom_value, "0"], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("Display cleared successfully")
                # Reset optimization state
                self.last_image_hash = None
                self.refresh_count = 0
                return True
            else:
                self.logger.error(f"Display clear failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Display clear failed: {e}")
            return False
    
    def _prepare_image(self, image: Image.Image) -> Image.Image:
        """Prepare image for display (resize and convert)"""
        # Resize image to display dimensions
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.LANCZOS)
        
        # Convert to 1-bit (black and white) for e-ink display
        if image.mode != '1':
            image = image.convert('1')
            
        return image
    
    def _should_skip_refresh(self, image: Image.Image) -> bool:
        """Check if refresh should be skipped based on image comparison"""
        # Calculate image hash for comparison
        image_bytes = image.tobytes()
        current_hash = hashlib.md5(image_bytes).hexdigest()
        
        # Compare with last image hash
        if current_hash == self.last_image_hash:
            return True
            
        return False
    
    def _get_refresh_mode(self, force_refresh: bool) -> str:
        """Determine the appropriate refresh mode"""
        # Force full refresh every N updates to prevent ghosting
        if force_refresh or (self.refresh_count % self.full_refresh_interval == 0):
            return "1"  # Full refresh mode
        else:
            return "1"  # For IT8951, we typically use mode 1
    
    def _update_optimization_state(self, image: Image.Image):
        """Update optimization state after successful display"""
        image_bytes = image.tobytes()
        self.last_image_hash = hashlib.md5(image_bytes).hexdigest()
        self.refresh_count += 1
    
    def get_display_info(self) -> dict:
        """Get display information"""
        return {
            'width': self.width,
            'height': self.height,
            'vcom_value': self.vcom_value,
            'driver_path': self.driver_path,
            'refresh_count': self.refresh_count,
            'last_hash': self.last_image_hash[:8] if self.last_image_hash else None
        }


class OptimizedWaveshareIT8951(WaveshareIT8951):
    """Extended version with additional optimizations"""
    
    def __init__(self, vcom_value: str = "-1.50", driver_path: str = None, 
                 enable_change_detection: bool = True, full_refresh_interval: int = 10):
        super().__init__(vcom_value, driver_path)
        self.enable_change_detection = enable_change_detection
        self.full_refresh_interval = full_refresh_interval
        
        # Performance tracking
        self.display_times = []
        self.skipped_refreshes = 0
        
    def display(self, image: Image.Image, force_refresh: bool = False) -> bool:
        """Enhanced display method with performance tracking"""
        import time
        
        start_time = time.time()
        
        # Use change detection if enabled
        if self.enable_change_detection and not force_refresh:
            if self._should_skip_refresh(self._prepare_image(image)):
                self.skipped_refreshes += 1
                self.logger.debug(f"Skipped refresh #{self.skipped_refreshes}")
                return True
        
        # Call parent display method
        result = super().display(image, force_refresh)
        
        # Track performance
        display_time = time.time() - start_time
        self.display_times.append(display_time)
        
        # Keep only last 10 measurements
        if len(self.display_times) > 10:
            self.display_times.pop(0)
            
        self.logger.debug(f"Display update took {display_time:.2f}s")
        
        return result
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        if not self.display_times:
            return {'avg_time': 0, 'min_time': 0, 'max_time': 0, 'skipped_refreshes': self.skipped_refreshes}
            
        return {
            'avg_time': sum(self.display_times) / len(self.display_times),
            'min_time': min(self.display_times),
            'max_time': max(self.display_times),
            'total_refreshes': self.refresh_count,
            'skipped_refreshes': self.skipped_refreshes,
            'efficiency': self.skipped_refreshes / (self.refresh_count + self.skipped_refreshes) if (self.refresh_count + self.skipped_refreshes) > 0 else 0
        }

