"""
Voice control module for Bible Clock.
Handles wake word detection and speech recognition.
"""

import threading
import time
import queue
import re
from typing import Optional, Callable, List
import config

# Voice recognition dependencies
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

class VoiceController:
    """Manages voice control with wake word detection and speech recognition."""
    
    def __init__(self, simulate: bool = False, debug: bool = False):
        """
        Initialize voice controller.
        
        Args:
            simulate: Run in simulation mode
            debug: Enable debug output
        """
        self.simulate = simulate
        self.debug = debug
        self.enabled = config.AUDIO_ENABLED and not simulate
        
        # Voice recognition components
        self.recognizer = None
        self.microphone = None
        self.porcupine = None
        
        # Threading and control
        self.listening_thread = None
        self.stop_listening = threading.Event()
        self.audio_queue = queue.Queue()
        
        # Callbacks
        self.wake_word_callback: Optional[Callable] = None
        self.command_callback: Optional[Callable[[str], None]] = None
        
        # State
        self.is_listening = False
        self.wake_word_detected = False
        
        if self.enabled:
            self._initialize_voice_recognition()
        elif self.debug:
            print("Voice control disabled (simulation mode or config)")
    
    def _initialize_voice_recognition(self):
        """Initialize speech recognition components."""
        try:
            if SPEECH_RECOGNITION_AVAILABLE:
                self.recognizer = sr.Recognizer()
                
                # Configure recognizer
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                self.recognizer.phrase_threshold = 0.3
                
                # Initialize microphone
                if PYAUDIO_AVAILABLE:
                    self.microphone = sr.Microphone()
                    
                    # Calibrate for ambient noise
                    with self.microphone as source:
                        if self.debug:
                            print("Calibrating microphone for ambient noise...")
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                if self.debug:
                    print("Speech recognition initialized")
            
            # Initialize wake word detection (Porcupine)
            if PORCUPINE_AVAILABLE:
                try:
                    # Note: This requires a Porcupine access key
                    # For now, we'll use a simple keyword detection fallback
                    if self.debug:
                        print("Porcupine wake word detection available")
                except Exception as e:
                    if self.debug:
                        print(f"Porcupine initialization failed: {e}")
            
        except Exception as e:
            if self.debug:
                print(f"Voice recognition initialization failed: {e}")
            self.enabled = False
    
    def start_listening(self):
        """Start listening for wake word and commands."""
        if not self.enabled or self.is_listening:
            return False
        
        self.stop_listening.clear()
        self.is_listening = True
        
        # Start listening thread
        self.listening_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listening_thread.start()
        
        if self.debug:
            print(f"Voice control started. Listening for wake word: '{config.WAKE_WORD}'")
        
        return True
    
    def stop_listening_for_commands(self):
        """Stop listening for voice commands."""
        self.stop_listening.set()
        self.is_listening = False
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2)
        
        if self.debug:
            print("Voice control stopped")
    
    def _listen_loop(self):
        """Main listening loop for wake word and commands."""
        while not self.stop_listening.is_set():
            try:
                if not self.wake_word_detected:
                    # Listen for wake word
                    self._listen_for_wake_word()
                else:
                    # Listen for command after wake word
                    self._listen_for_command()
                    
            except Exception as e:
                if self.debug:
                    print(f"Voice listening error: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def _listen_for_wake_word(self):
        """Listen for the wake word."""
        if not self.microphone or not self.recognizer:
            time.sleep(1)
            return
        
        try:
            # Listen for audio
            with self.microphone as source:
                # Short timeout to allow checking stop_listening
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language='en-US').lower()
                
                if self.debug:
                    print(f"Heard: '{text}'")
                
                # Check for wake word
                if self._contains_wake_word(text):
                    self.wake_word_detected = True
                    if self.debug:
                        print(f"Wake word '{config.WAKE_WORD}' detected!")
                    
                    # Call wake word callback
                    if self.wake_word_callback:
                        self.wake_word_callback()
                    
                    # Start timer for command timeout
                    self._start_command_timeout()
                    
            except sr.UnknownValueError:
                # No speech detected, continue listening
                pass
            except sr.RequestError as e:
                if self.debug:
                    print(f"Speech recognition error: {e}")
                
        except sr.WaitTimeoutError:
            # Timeout is normal, continue listening
            pass
    
    def _listen_for_command(self):
        """Listen for voice command after wake word."""
        if not self.microphone or not self.recognizer:
            time.sleep(1)
            return
        
        try:
            # Listen for command
            with self.microphone as source:
                if self.debug:
                    print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=config.VOICE_TIMEOUT, phrase_time_limit=5)
            
            # Recognize command
            try:
                command = self.recognizer.recognize_google(audio, language='en-US').lower()
                
                if self.debug:
                    print(f"Command received: '{command}'")
                
                # Process command
                self._process_voice_command(command)
                
            except sr.UnknownValueError:
                if self.debug:
                    print("Could not understand command")
            except sr.RequestError as e:
                if self.debug:
                    print(f"Command recognition error: {e}")
            
        except sr.WaitTimeoutError:
            if self.debug:
                print("Command timeout - no speech detected")
        
        # Reset wake word detection
        self.wake_word_detected = False
    
    def _contains_wake_word(self, text: str) -> bool:
        """
        Check if text contains the wake word.
        
        Args:
            text: Text to check
            
        Returns:
            True if wake word is detected
        """
        wake_word = config.WAKE_WORD.lower()
        
        # Simple keyword matching
        if wake_word in text:
            return True
        
        # Handle variations
        wake_variations = [
            "hey bible",
            "a bible", 
            "hey bibles",
            "bible"
        ]
        
        for variation in wake_variations:
            if variation in text:
                return True
        
        return False
    
    def _process_voice_command(self, command: str):
        """
        Process recognized voice command.
        
        Args:
            command: Recognized command text
        """
        command = command.lower().strip()
        
        # Define command patterns
        read_patterns = [
            r"read.*verse",
            r"read.*that",
            r"speak.*verse",
            r"say.*verse",
            r"tell.*verse"
        ]
        
        explain_patterns = [
            r"tell.*more",
            r"explain.*verse",
            r"what.*mean",
            r"more.*about",
            r"help.*understand"
        ]
        
        expand_patterns = [
            r"expand",
            r"show.*more",
            r"continue.*chapter",
            r"rest.*chapter",
            r"more.*verses"
        ]
        
        # Check for read command
        for pattern in read_patterns:
            if re.search(pattern, command):
                if self.debug:
                    print("Voice command: Read verse")
                if self.command_callback:
                    self.command_callback("read_verse")
                return
        
        # Check for explain command
        for pattern in explain_patterns:
            if re.search(pattern, command):
                if self.debug:
                    print("Voice command: Explain verse")
                if self.command_callback:
                    self.command_callback("explain_verse")
                return
        
        # Check for expand command
        for pattern in expand_patterns:
            if re.search(pattern, command):
                if self.debug:
                    print("Voice command: Expand chapter")
                if self.command_callback:
                    self.command_callback("expand_chapter")
                return
        
        # Default response for unrecognized commands
        if self.debug:
            print(f"Unrecognized command: '{command}'")
        if self.command_callback:
            self.command_callback("unknown")
    
    def _start_command_timeout(self):
        """Start timeout timer for voice commands."""
        def timeout_handler():
            time.sleep(config.VOICE_TIMEOUT)
            if self.wake_word_detected:
                self.wake_word_detected = False
                if self.debug:
                    print("Voice command timeout")
        
        timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        timeout_thread.start()
    
    def simulate_wake_word(self):
        """Simulate wake word detection for testing."""
        if self.debug:
            print(f"Simulating wake word: '{config.WAKE_WORD}'")
        
        self.wake_word_detected = True
        if self.wake_word_callback:
            self.wake_word_callback()
    
    def simulate_voice_command(self, command: str):
        """
        Simulate voice command for testing.
        
        Args:
            command: Command to simulate
        """
        if self.debug:
            print(f"Simulating voice command: '{command}'")
        
        self._process_voice_command(command)
    
    def set_wake_word_callback(self, callback: Callable[[], None]):
        """
        Set callback for wake word detection.
        
        Args:
            callback: Function to call when wake word is detected
        """
        self.wake_word_callback = callback
    
    def set_command_callback(self, callback: Callable[[str], None]):
        """
        Set callback for voice commands.
        
        Args:
            callback: Function to call with recognized commands
        """
        self.command_callback = callback
    
    def get_status(self) -> dict:
        """
        Get voice control status.
        
        Returns:
            Dictionary with voice control status
        """
        return {
            'enabled': self.enabled,
            'simulate': self.simulate,
            'is_listening': self.is_listening,
            'wake_word_detected': self.wake_word_detected,
            'wake_word': config.WAKE_WORD,
            'voice_timeout': config.VOICE_TIMEOUT,
            'components_available': {
                'speech_recognition': SPEECH_RECOGNITION_AVAILABLE,
                'pyaudio': PYAUDIO_AVAILABLE,
                'porcupine': PORCUPINE_AVAILABLE
            },
            'microphone_available': self.microphone is not None,
            'recognizer_available': self.recognizer is not None
        }
    
    def cleanup(self):
        """Clean up voice control resources."""
        try:
            self.stop_listening_for_commands()
            
            if self.porcupine:
                self.porcupine.delete()
                
        except Exception as e:
            if self.debug:
                print(f"Voice control cleanup error: {e}")

