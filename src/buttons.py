"""
Button controls module for the Bible Clock.
Enhanced with mode cycling and version toggle functionality.
"""

import time
import threading
from typing import Callable, Optional
import config

# Mock GPIO for simulation
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    # Use fake GPIO for simulation
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        PUD_UP = "PUD_UP"
        FALLING = "FALLING"
        
        def setmode(self, mode): pass
        def setup(self, pin, mode, pull_up_down=None): pass
        def add_event_detect(self, pin, edge, callback=None, bouncetime=None): pass
        def cleanup(self): pass
        def input(self, pin): return True
    
    GPIO = MockGPIO()
    GPIO_AVAILABLE = False


class ButtonManager:
    """Manages button inputs for mode cycling and version toggle."""
    
    def __init__(self, simulate: bool = None):
        """
        Initialize button manager.
        
        Args:
            simulate: Force simulation mode. Uses config.SIMULATE if None.
        """
        self.simulate = simulate if simulate is not None else config.SIMULATE
        self.mode_callback: Optional[Callable] = None
        self.version_callback: Optional[Callable] = None
        self.verse_cycle_callback: Optional[Callable] = None
        
        # Current states
        self.current_mode = config.CLOCK_MODE
        self.current_version = config.KJV_ONLY
        
        # Button press tracking
        self.last_button1_press = 0
        self.last_button2_press = 0
        self.debounce_time = getattr(config, 'BUTTON_DEBOUNCE_TIME', 300)  # Default 300ms
        
        if not self.simulate and GPIO_AVAILABLE:
            self._setup_gpio()
        else:
            if config.DEBUG:
                print("Button manager in simulation mode")
    
    def _setup_gpio(self):
        """Setup GPIO pins for button inputs."""
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Setup button pins
            GPIO.setup(getattr(config, 'BUTTON1_PIN', 18), GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(getattr(config, 'BUTTON2_PIN', 19), GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Add event detection
            GPIO.add_event_detect(getattr(config, 'BUTTON1_PIN', 18), GPIO.FALLING, 
                                callback=self._button1_pressed, 
                                bouncetime=self.debounce_time)
            GPIO.add_event_detect(getattr(config, 'BUTTON2_PIN', 19), GPIO.FALLING, 
                                callback=self._button2_pressed, 
                                bouncetime=self.debounce_time)
            
            if config.DEBUG:
                print(f"GPIO setup complete. Button 1: Pin {getattr(config, 'BUTTON1_PIN', 18)}, Button 2: Pin {getattr(config, 'BUTTON2_PIN', 19)}")
        
        except Exception as e:
            print(f"GPIO setup failed: {e}")
            self.simulate = True
    
    def _button1_pressed(self, channel):
        """Handle Button 1 press - Mode cycling (Clock ↔ Day)."""
        current_time = time.time()
        if current_time - self.last_button1_press < (self.debounce_time / 1000.0):
            return  # Ignore bounce
        
        self.last_button1_press = current_time
        
        # Cycle between clock and day modes
        if self.current_mode == config.CLOCK_MODE:
            self.current_mode = config.DAY_MODE
        else:
            self.current_mode = config.CLOCK_MODE
        
        if config.DEBUG:
            print(f"Button 1 pressed: Mode changed to {self.current_mode}")
        
        # Call the mode change callback
        if self.mode_callback:
            self.mode_callback(self.current_mode)
    
    def _button2_pressed(self, channel):
        """Handle Button 2 press - Version toggle (KJV ↔ KJV+Amplified)."""
        current_time = time.time()
        if current_time - self.last_button2_press < (self.debounce_time / 1000.0):
            return  # Ignore bounce
        
        self.last_button2_press = current_time
        
        # Toggle between KJV only and KJV+Amplified
        if self.current_version == config.KJV_ONLY:
            self.current_version = config.KJV_AMPLIFIED
        else:
            self.current_version = config.KJV_ONLY
        
        if config.DEBUG:
            print(f"Button 2 pressed: Version changed to {self.current_version}")
        
        # Call the version change callback
        if self.version_callback:
            self.version_callback(self.current_version)
    
    def simulate_button1_press(self):
        """Simulate Button 1 press for testing."""
        if config.DEBUG:
            print("Simulating Button 1 press (Mode cycle)")
        self._button1_pressed(None)
    
    def simulate_button2_press(self):
        """Simulate Button 2 press for testing."""
        if config.DEBUG:
            print("Simulating Button 2 press (Version toggle)")
        self._button2_pressed(None)
    
    def set_mode_callback(self, callback: Callable[[str], None]):
        """
        Set callback for mode changes.
        
        Args:
            callback: Function to call when mode changes. Receives new mode as parameter.
        """
        self.mode_callback = callback
    
    def set_version_callback(self, callback: Callable[[str], None]):
        """
        Set callback for version changes.
        
        Args:
            callback: Function to call when version changes. Receives new version as parameter.
        """
        self.version_callback = callback
    
    def set_verse_cycle_callback(self, callback: Callable[[], None]):
        """
        Set callback for verse cycling (if needed for future features).
        
        Args:
            callback: Function to call when cycling verses manually.
        """
        self.verse_cycle_callback = callback
    
    def get_current_mode(self) -> str:
        """Get the current display mode."""
        return self.current_mode
    
    def get_current_version(self) -> str:
        """Get the current version display setting."""
        return self.current_version
    
    def set_mode(self, mode: str):
        """
        Set the current mode programmatically.
        
        Args:
            mode: New mode (CLOCK_MODE or DAY_MODE)
        """
        if mode in [config.CLOCK_MODE, config.DAY_MODE]:
            self.current_mode = mode
            if config.DEBUG:
                print(f"Mode set to: {mode}")
    
    def set_version(self, version: str):
        """
        Set the current version programmatically.
        
        Args:
            version: New version (KJV_ONLY or KJV_AMPLIFIED)
        """
        if version in [config.KJV_ONLY, config.KJV_AMPLIFIED]:
            self.current_version = version
            if config.DEBUG:
                print(f"Version set to: {version}")
    
    def get_status(self) -> dict:
        """
        Get current button status and settings.
        
        Returns:
            Dictionary with button status information
        """
        return {
            'simulate': self.simulate,
            'gpio_available': GPIO_AVAILABLE,
            'current_mode': self.current_mode,
            'current_version': self.current_version,
            'button1_pin': getattr(config, 'BUTTON1_PIN', 18),
            'button2_pin': getattr(config, 'BUTTON2_PIN', 19),
            'debounce_time': self.debounce_time
        }
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if not self.simulate and GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
                if config.DEBUG:
                    print("GPIO cleanup completed")
            except Exception as e:
                print(f"GPIO cleanup error: {e}")
    
    def __del__(self):
        """Destructor to ensure GPIO cleanup."""
        self.cleanup()

