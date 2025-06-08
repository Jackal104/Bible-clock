"""
Audio and Text-to-Speech module for Bible Clock.
Supports ReSpeaker HAT and various TTS engines.
"""

import os
import threading
import time
from typing import Optional, Callable
import config

# Audio dependencies
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import subprocess
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

class AudioManager:
    """Manages audio output and text-to-speech functionality."""
    
    def __init__(self, simulate: bool = False, debug: bool = False):
        """
        Initialize audio manager.
        
        Args:
            simulate: Run in simulation mode (no actual audio)
            debug: Enable debug output
        """
        self.simulate = simulate
        self.debug = debug
        self.enabled = config.AUDIO_ENABLED and not simulate
        self.tts_engine = None
        self.audio_lock = threading.Lock()
        
        if self.enabled:
            self._initialize_tts()
        elif self.debug:
            print("Audio disabled (simulation mode or config)")
    
    def _initialize_tts(self):
        """Initialize text-to-speech engine."""
        try:
            if config.TTS_ENGINE == 'pyttsx3' and PYTTSX3_AVAILABLE:
                self.tts_engine = pyttsx3.init()
                
                # Configure voice settings
                self.tts_engine.setProperty('rate', config.TTS_VOICE_RATE)
                self.tts_engine.setProperty('volume', config.TTS_VOICE_VOLUME)
                
                # Try to set a good voice
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    # Prefer female voice if available
                    for voice in voices:
                        if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                    else:
                        # Use first available voice
                        self.tts_engine.setProperty('voice', voices[0].id)
                
                if self.debug:
                    print("pyttsx3 TTS engine initialized")
                    
            elif config.TTS_ENGINE == 'espeak':
                # espeak is usually available on Linux
                if self.debug:
                    print("Using espeak TTS engine")
                    
            elif config.TTS_ENGINE == 'festival':
                # festival TTS
                if self.debug:
                    print("Using festival TTS engine")
            else:
                if self.debug:
                    print(f"TTS engine {config.TTS_ENGINE} not available, using fallback")
                    
        except Exception as e:
            if self.debug:
                print(f"Failed to initialize TTS: {e}")
            self.enabled = False
    
    def speak_text(self, text: str, blocking: bool = False) -> bool:
        """
        Speak the given text using TTS.
        
        Args:
            text: Text to speak
            blocking: Whether to wait for speech to complete
            
        Returns:
            True if speech was initiated successfully, False otherwise
        """
        if not self.enabled:
            if self.debug:
                print(f"TTS (simulated): {text}")
            return True
        
        if not text or not text.strip():
            return False
        
        try:
            with self.audio_lock:
                if self.tts_engine and config.TTS_ENGINE == 'pyttsx3':
                    if blocking:
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    else:
                        # Run in separate thread for non-blocking
                        def speak_async():
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                        
                        thread = threading.Thread(target=speak_async, daemon=True)
                        thread.start()
                        
                elif config.TTS_ENGINE == 'espeak':
                    # Use espeak command line
                    cmd = [
                        'espeak', 
                        '-s', str(config.TTS_VOICE_RATE),
                        '-a', str(int(config.TTS_VOICE_VOLUME * 200)),
                        text
                    ]
                    
                    if blocking:
                        subprocess.run(cmd, check=True)
                    else:
                        subprocess.Popen(cmd)
                        
                elif config.TTS_ENGINE == 'festival':
                    # Use festival command line
                    if blocking:
                        process = subprocess.Popen(['festival', '--tts'], 
                                                 stdin=subprocess.PIPE, 
                                                 text=True)
                        process.communicate(input=text)
                    else:
                        process = subprocess.Popen(['festival', '--tts'], 
                                                 stdin=subprocess.PIPE, 
                                                 text=True)
                        process.stdin.write(text)
                        process.stdin.close()
                
                if self.debug:
                    print(f"TTS: {text[:50]}{'...' if len(text) > 50 else ''}")
                
                return True
                
        except Exception as e:
            if self.debug:
                print(f"TTS error: {e}")
            return False
    
    def speak_verse(self, book: str, verse_ref: str, verse_text: str, mode: str = None) -> bool:
        """
        Speak a Bible verse with proper formatting.
        
        Args:
            book: Book name
            verse_ref: Verse reference (e.g., "John 3:16")
            verse_text: Verse text
            mode: Current mode (for context)
            
        Returns:
            True if speech was initiated successfully
        """
        # Format the speech text
        if mode == config.DAY_MODE:
            intro = f"Today's verse from {verse_ref}:"
        else:
            intro = f"From {verse_ref}:"
        
        # Combine intro and verse
        full_text = f"{intro} {verse_text}"
        
        return self.speak_text(full_text, blocking=False)
    
    def speak_explanation(self, explanation: str) -> bool:
        """
        Speak a verse explanation from ChatGPT.
        
        Args:
            explanation: Explanation text to speak
            
        Returns:
            True if speech was initiated successfully
        """
        intro = "Here's more about that verse: "
        full_text = f"{intro} {explanation}"
        
        return self.speak_text(full_text, blocking=False)
    
    def test_audio(self) -> bool:
        """
        Test audio functionality.
        
        Returns:
            True if audio test successful
        """
        test_text = "Bible Clock audio test. Can you hear this?"
        return self.speak_text(test_text, blocking=True)
    
    def stop_speech(self):
        """Stop any ongoing speech."""
        try:
            if self.tts_engine and config.TTS_ENGINE == 'pyttsx3':
                self.tts_engine.stop()
        except Exception as e:
            if self.debug:
                print(f"Error stopping speech: {e}")
    
    def get_status(self) -> dict:
        """
        Get audio system status.
        
        Returns:
            Dictionary with audio status information
        """
        return {
            'enabled': self.enabled,
            'simulate': self.simulate,
            'tts_engine': config.TTS_ENGINE,
            'tts_available': self.tts_engine is not None,
            'pyttsx3_available': PYTTSX3_AVAILABLE,
            'pyaudio_available': PYAUDIO_AVAILABLE,
            'voice_rate': config.TTS_VOICE_RATE,
            'voice_volume': config.TTS_VOICE_VOLUME,
            'respeaker_configured': {
                'channels': config.RESPEAKER_CHANNELS,
                'rate': config.RESPEAKER_RATE,
                'chunk': config.RESPEAKER_CHUNK
            }
        }
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            if self.tts_engine:
                self.stop_speech()
        except Exception as e:
            if self.debug:
                print(f"Audio cleanup error: {e}")


class ReSpeakerManager:
    """Manages ReSpeaker HAT for audio input/output."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize ReSpeaker manager.
        
        Args:
            debug: Enable debug output
        """
        self.debug = debug
        self.audio = None
        self.available = PYAUDIO_AVAILABLE
        
        if self.available:
            self._initialize_respeaker()
    
    def _initialize_respeaker(self):
        """Initialize ReSpeaker HAT."""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find ReSpeaker device
            device_index = self._find_respeaker_device()
            if device_index is not None:
                if self.debug:
                    print(f"ReSpeaker device found at index {device_index}")
            else:
                if self.debug:
                    print("ReSpeaker device not found, using default")
                    
        except Exception as e:
            if self.debug:
                print(f"Failed to initialize ReSpeaker: {e}")
            self.available = False
    
    def _find_respeaker_device(self) -> Optional[int]:
        """
        Find ReSpeaker device index.
        
        Returns:
            Device index if found, None otherwise
        """
        if not self.audio:
            return None
            
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if 'respeaker' in device_info['name'].lower():
                    return i
        except Exception as e:
            if self.debug:
                print(f"Error finding ReSpeaker device: {e}")
        
        return None
    
    def get_status(self) -> dict:
        """
        Get ReSpeaker status.
        
        Returns:
            Dictionary with ReSpeaker status
        """
        status = {
            'available': self.available,
            'pyaudio_available': PYAUDIO_AVAILABLE,
            'device_found': False,
            'device_index': None
        }
        
        if self.available:
            device_index = self._find_respeaker_device()
            status['device_found'] = device_index is not None
            status['device_index'] = device_index
        
        return status
    
    def cleanup(self):
        """Clean up ReSpeaker resources."""
        try:
            if self.audio:
                self.audio.terminate()
        except Exception as e:
            if self.debug:
                print(f"ReSpeaker cleanup error: {e}")

