"""
Enhanced Display Manager

This module manages the e-ink display with optimizations, error handling,
and support for both hardware and simulation modes.
"""

import logging
import gc
import psutil
import os
from typing import Optional, Dict, Any
from PIL import Image
from config import config
from waveshare_wrapper import OptimizedWaveshareIT8951
from image_generator import ImageGenerator

class DisplayManager:
    """Enhanced display manager with optimization and error handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.epd = None
        self.image_generator = None
        self.simulation_mode = config.SIMULATION_MODE
        
        # Performance tracking
        self.display_count = 0
        self.error_count = 0
        self.last_error = None
        
        # Memory management
        self.memory_threshold = config.MEMORY_LIMIT_MB * 1024 * 1024  # Convert to bytes
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize display and image generator components"""
        try:
            # Initialize image generator
            self.image_generator = ImageGenerator(
                width=config.DISPLAY_WIDTH,
                height=config.DISPLAY_HEIGHT,
                font_path=config.FONT_PATH
            )
            self.logger.info("Image generator initialized")
            
            # Initialize display
            if not self.simulation_mode:
                self._init_eink()
            else:
                self.logger.info("Running in simulation mode - no hardware display")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize display components: {e}")
            self.simulation_mode = True
    
    def _init_eink(self):
        """Initialize e-ink display (Raspberry Pi only)"""
        try:
            # Update VCOM value from file if available
            config.update_vcom_value()
            
            # Initialize display with optimizations
            self.epd = OptimizedWaveshareIT8951(
                vcom_value=config.VCOM_VALUE,
                driver_path=config.DRIVER_PATH,
                enable_change_detection=config.REFRESH_OPTIMIZATION,
                full_refresh_interval=config.FULL_REFRESH_INTERVAL
            )
            
            if self.epd.init():
                self.logger.info(f"E-ink display initialized with VCOM {config.VCOM_VALUE}")
                
                # Clear display on initialization
                self.epd.clear()
                self.logger.info("Display cleared and ready")
            else:
                raise Exception("Display initialization failed")
                
        except ImportError as e:
            self.logger.error(f"Failed to import display driver: {e}")
            self.simulation_mode = True
        except Exception as e:
            self.logger.error(f"Display initialization error: {e}")
            self.last_error = str(e)
            self.error_count += 1
            self.simulation_mode = True
    
    def display_verse(self, verse_data: Dict[str, str], force_refresh: bool = False) -> bool:
        """
        Display verse on screen
        
        Args:
            verse_data: Formatted verse data
            force_refresh: Force display refresh regardless of optimization
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Displaying verse: {verse_data.get('reference', 'Unknown')}")
            
            # Generate image
            image = self.image_generator.generate_verse_image(verse_data)
            
            if self.simulation_mode:
                return self._simulate_display(image, verse_data)
            else:
                return self._display_on_hardware(image, force_refresh)
                
        except Exception as e:
            self.logger.error(f"Failed to display verse: {e}")
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    def _display_on_hardware(self, image: Image.Image, force_refresh: bool = False) -> bool:
        """Display image on hardware"""
        try:
            if not self.epd:
                self.logger.error("Display not initialized")
                return False
            
            # Check memory usage before display
            self._check_memory_usage()
            
            # Display image
            success = self.epd.display(image, force_refresh)
            
            if success:
                self.display_count += 1
                self.logger.debug(f"Display update #{self.display_count} successful")
            else:
                self.error_count += 1
                self.logger.error("Display update failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Hardware display error: {e}")
            self.last_error = str(e)
            self.error_count += 1
            return False
    
    def _simulate_display(self, image: Image.Image, verse_data: Dict[str, str]) -> bool:
        """Simulate display for testing"""
        try:
            # Save image for inspection
            output_path = f"/tmp/bible_clock_display_{self.display_count:04d}.png"
            image.save(output_path)
            
            self.display_count += 1
            
            self.logger.info(f"Simulation: Displayed verse '{verse_data.get('reference', 'Unknown')}'")
            self.logger.info(f"Simulation: Image saved to {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
            self.error_count += 1
            return False
    
    def display_error(self, error_message: str = "Unable to load verse") -> bool:
        """Display error message"""
        try:
            self.logger.warning(f"Displaying error message: {error_message}")
            
            # Generate error image
            image = self.image_generator.generate_error_image(error_message)
            
            if self.simulation_mode:
                return self._simulate_display(image, {'reference': 'Error', 'text': error_message})
            else:
                return self._display_on_hardware(image, force_refresh=True)
                
        except Exception as e:
            self.logger.error(f"Failed to display error message: {e}")
            return False
    
    def clear_display(self) -> bool:
        """Clear the display"""
        try:
            if self.simulation_mode:
                self.logger.info("Simulation: Display cleared")
                return True
            elif self.epd:
                success = self.epd.clear()
                if success:
                    self.logger.info("Display cleared")
                else:
                    self.logger.error("Failed to clear display")
                return success
            else:
                self.logger.error("Display not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to clear display: {e}")
            return False
    
    def _check_memory_usage(self):
        """Check and manage memory usage"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            if memory_info.rss > self.memory_threshold:
                self.logger.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
                
                # Force garbage collection
                gc.collect()
                
                # Log memory after cleanup
                memory_info_after = process.memory_info()
                self.logger.info(f"Memory after cleanup: {memory_info_after.rss / 1024 / 1024:.1f} MB")
                
        except Exception as e:
            self.logger.warning(f"Memory check failed: {e}")
    
    def get_display_stats(self) -> Dict[str, Any]:
        """Get display statistics"""
        stats = {
            'simulation_mode': self.simulation_mode,
            'display_count': self.display_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'success_rate': (self.display_count / (self.display_count + self.error_count)) if (self.display_count + self.error_count) > 0 else 0
        }
        
        # Add hardware-specific stats
        if not self.simulation_mode and self.epd:
            try:
                stats.update({
                    'display_info': self.epd.get_display_info(),
                    'performance_stats': self.epd.get_performance_stats()
                })
            except Exception as e:
                self.logger.warning(f"Failed to get hardware stats: {e}")
        
        # Add image generator stats
        if self.image_generator:
            try:
                stats['font_info'] = self.image_generator.get_font_info()
            except Exception as e:
                self.logger.warning(f"Failed to get font info: {e}")
        
        return stats
    
    def test_display(self) -> Dict[str, Any]:
        """Test display functionality"""
        test_results = {
            'initialization': False,
            'image_generation': False,
            'display_update': False,
            'clear_display': False,
            'errors': []
        }
        
        try:
            # Test initialization
            if self.epd or self.simulation_mode:
                test_results['initialization'] = True
            else:
                test_results['errors'].append("Display not initialized")
            
            # Test image generation
            if self.image_generator:
                test_verse = {
                    'time': '12:00 PM',
                    'date': 'Test Date',
                    'reference': 'Test 1:1',
                    'text': 'This is a test verse for display testing.',
                    'translation': 'TEST',
                    'source': 'test'
                }
                
                try:
                    test_image = self.image_generator.generate_verse_image(test_verse)
                    test_results['image_generation'] = True
                except Exception as e:
                    test_results['errors'].append(f"Image generation failed: {e}")
            else:
                test_results['errors'].append("Image generator not available")
            
            # Test display update
            if test_results['image_generation']:
                try:
                    success = self.display_verse(test_verse, force_refresh=True)
                    test_results['display_update'] = success
                    if not success:
                        test_results['errors'].append("Display update failed")
                except Exception as e:
                    test_results['errors'].append(f"Display update error: {e}")
            
            # Test clear display
            try:
                success = self.clear_display()
                test_results['clear_display'] = success
                if not success:
                    test_results['errors'].append("Clear display failed")
            except Exception as e:
                test_results['errors'].append(f"Clear display error: {e}")
                
        except Exception as e:
            test_results['errors'].append(f"Test error: {e}")
        
        # Overall test result
        test_results['overall_success'] = (
            test_results['initialization'] and
            test_results['image_generation'] and
            test_results['display_update'] and
            test_results['clear_display']
        )
        
        return test_results
    
    def shutdown(self):
        """Shutdown display manager"""
        try:
            self.logger.info("Shutting down display manager")
            
            # Clear display before shutdown
            self.clear_display()
            
            # Clean up resources
            if self.epd:
                self.epd = None
            
            if self.image_generator:
                self.image_generator = None
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("Display manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Global display manager instance
display_manager = DisplayManager()

