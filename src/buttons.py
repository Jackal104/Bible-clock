"""
Button controls module for the Bible Clock.
Enhanced with mode cycling, version toggle, and audio/voice functionality.
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
    """Manages button inputs for mode cycling, version toggle, and audio/voice control."""
    
    def __init__(self, simulate: bool = None):
        """
        Initialize button manager.
        
        Args:
            simulate: Force simulation mode. Uses config.SIMULATE if None.
        """
        self.simulate = simulate if simulate is not None else config.SIMULATE
        self.mode_callback: Optional[Callable] = None
        self.version_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None  # NEW: Third button callback
        self.verse_cycle_callback: Optional[Callable] = None
        
        # Current states
        self.current_mode = config.CLOCK_MODE
        self.current_version = config.KJV_ONLY
        
        # Button press tracking
        self.last_button1_press = 0
        self.last_button2_press = 0
        self.last_button3_press = 0  # NEW: Third button tracking
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
            GPIO.setup(getattr(config, 'BUTTON_1_PIN', 18), GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(getattr(config, 'BUTTON_2_PIN', 19), GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(getattr(config, 'BUTTON_3_PIN', 20), GPIO.IN, pull_up_down=GPIO.PUD_UP)  # NEW: Third button
            
            # Add event detection
            GPIO.add_event_detect(getattr(config, 'BUTTON_1_PIN', 18), GPIO.FALLING, 
                                callback=self._button1_pressed, 
                                bouncetime=self.debounce_time)
            GPIO.add_event_detect(getattr(config, 'BUTTON_2_PIN', 19), GPIO.FALLING, 
                                callback=self._button2_pressed, 
                                bouncetime=self.debounce_time)
            GPIO.add_event_detect(getattr(config, 'BUTTON_3_PIN', 20), GPIO.FALLING,  # NEW: Third button event
                                callback=self._button3_pressed, 
                                bouncetime=self.debounce_time)
            
            if config.DEBUG:
                print(f"GPIO setup complete. Button 1: Pin {getattr(config, 'BUTTON_1_PIN', 18)}, "
                      f"Button 2: Pin {getattr(config, 'BUTTON_2_PIN', 19)}, "
                      f"Button 3: Pin {getattr(config, 'BUTTON_3_PIN', 20)}")
        
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
    
    def _button3_pressed(self, channel):
        """Handle Button 3 press - Audio/Voice activation (TTS, Voice Commands, ChatGPT)."""
        current_time = time.time()
        if current_time - self.last_button3_press < (self.debounce_time / 1000.0):
            return  # Ignore bounce
        
        self.last_button3_press = current_time
        
        if config.DEBUG:
            print("Button 3 pressed: Audio/Voice activation")
        
        # Call the audio callback
        if self.audio_callback:
            self.audio_callback()
    
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
    
    def simulate_button3_press(self):
        """Simulate Button 3 press for testing."""
        if config.DEBUG:
            print("Simulating Button 3 press (Audio/Voice)")
        self._button3_pressed(None)
    
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
    
    def set_audio_callback(self, callback: Callable[[], None]):
        """
        Set callback for audio/voice activation.
        
        Args:
            callback: Function to call when audio button is pressed.
        """
        self.audio_callback = callback
    
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
            'button1_pin': getattr(config, 'BUTTON_1_PIN', 18),
            'button2_pin': getattr(config, 'BUTTON_2_PIN', 19),
            'button3_pin': getattr(config, 'BUTTON_3_PIN', 20),  # NEW: Third button pin
            'debounce_time': self.debounce_time,
            'audio_callback_set': self.audio_callback is not None  # NEW: Audio callback status
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

