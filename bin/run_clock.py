#!/usr/bin/env python3
"""
Bible Clock - Enhanced Version
A digital clock that displays Bible verses corresponding to the current time.

Features:
- Time-based verse display (hour:minute = chapter:verse)
- Auto-resizing text to fit display
- Temporary mode indicators (3 seconds)
- Random Bible book summaries at :00 minutes
- Three-button control (Mode, Version, Audio/Voice)
- Cross-platform font support
- Audio, voice, and ChatGPT integration
- Side-by-side KJV + Amplified display
"""

import sys
import os
import signal
import argparse
import time
from datetime import datetime
from typing import Optional, Tuple

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config
from display import DisplayManager
from buttons import ButtonManager
from bible_book_verse_selector import BibleBookVerseSelector

# Import audio and voice components with error handling
try:
    from audio_manager import AudioManager
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    AudioManager = None

try:
    from voice_controller import VoiceController
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    VoiceController = None

try:
    from chatgpt_explainer import ChatGPTExplainer
    CHATGPT_AVAILABLE = True
except ImportError:
    CHATGPT_AVAILABLE = False
    ChatGPTExplainer = None


class BibleClock:
    """Main Bible Clock application with enhanced features."""
    
    def __init__(self, simulate: bool = None, debug: bool = None):
        """
        Initialize the Bible Clock.
        
        Args:
            simulate: Force simulation mode. Uses config.SIMULATE if None.
            debug: Force debug mode. Uses config.DEBUG if None.
        """
        self.simulate = simulate if simulate is not None else config.SIMULATE
        self.debug = debug if debug is not None else config.DEBUG
        self.running = False
        
        # Current state
        self.current_mode = config.DEFAULT_MODE
        self.current_version = config.DEFAULT_VERSION
        self.current_verse_data = None
        
        # Initialize components
        self.display = DisplayManager(simulate=self.simulate)
        self.verse_selector = BibleBookVerseSelector()
        self.buttons = ButtonManager(simulate=self.simulate)
        
        # Initialize audio components
        if AUDIO_AVAILABLE:
            self.audio_manager = AudioManager(simulate=self.simulate, debug=self.debug)
        else:
            self.audio_manager = None
            if self.debug:
                print("Audio manager not available")
        
        # Initialize voice controller
        if VOICE_AVAILABLE:
            self.voice_controller = VoiceController(simulate=self.simulate, debug=self.debug)
        else:
            self.voice_controller = None
            if self.debug:
                print("Voice controller not available")
        
        # Initialize ChatGPT explainer
        if CHATGPT_AVAILABLE:
            self.chatgpt_explainer = ChatGPTExplainer(debug=self.debug)
        else:
            self.chatgpt_explainer = None
            if self.debug:
                print("ChatGPT explainer not available")
        
        # Setup button callbacks
        self.buttons.set_mode_callback(self._on_mode_change)
        self.buttons.set_version_callback(self._on_version_change)
        
        # Setup third button callback if audio is available
        if hasattr(self.buttons, 'set_audio_callback'):
            self.buttons.set_audio_callback(self._on_audio_button)
        
        # Setup voice command callback if voice controller is available
        if self.voice_controller and hasattr(self.voice_controller, 'set_command_callback'):
            self.voice_controller.set_command_callback(self._on_voice_command)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if self.debug:
            print("Bible Clock initialized successfully!")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.stop()
    
    def _on_mode_change(self, new_mode: str):
        """Handle mode change from button press."""
        self.current_mode = new_mode
        if self.debug:
            print(f"Mode changed to: {new_mode}")
        
        # Trigger temporary mode display
        if hasattr(self.display, 'trigger_mode_display'):
            self.display.trigger_mode_display(f"Mode: {new_mode.title()}")
        
        # Immediately update display with new mode
        self._update_display()
    
    def _on_version_change(self, new_version: str):
        """Handle version change from button press."""
        self.current_version = new_version
        if self.debug:
            print(f"Version changed to: {new_version}")
        
        # Trigger temporary mode display for version change
        version_text = f"Version: {new_version.replace('_', ' ').title()}"
        if hasattr(self.display, 'trigger_mode_display'):
            self.display.trigger_mode_display(version_text)
        
        # Immediately update display with new version
        self._update_display()
    
    def _on_audio_button(self):
        """Handle third button press - Audio/TTS/Voice activation."""
        if self.debug:
            print("Audio button pressed")
        
        # Show audio mode indicator
        if hasattr(self.display, 'trigger_mode_display'):
            self.display.trigger_mode_display("Audio Mode")
        
        # Read current verse aloud if audio is available
        if self.audio_manager and self.current_verse_data:
            try:
                book, reference, text = self.current_verse_data
                full_text = f"{reference}. {text}"
                if hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(full_text)
            except Exception as e:
                if self.debug:
                    print(f"Audio playback error: {e}")
        
        # Activate voice listening if available
        if self.voice_controller:
            try:
                if hasattr(self.voice_controller, 'start_listening'):
                    self.voice_controller.start_listening()
            except Exception as e:
                if self.debug:
                    print(f"Voice activation error: {e}")
    
    def _on_voice_command(self, command: str):
        """Handle voice commands from wake word detection."""
        if self.debug:
            print(f"Voice command received: {command}")
        
        command_lower = command.lower()
        
        if "explain" in command_lower or "meaning" in command_lower:
            self._handle_explain_command()
        elif "repeat" in command_lower or "read again" in command_lower:
            self._handle_repeat_command()
        elif "reference" in command_lower:
            self._handle_reference_command()
        elif "mode" in command_lower:
            self._handle_mode_command()
        elif "time" in command_lower:
            self._handle_time_command()
        elif "expand" in command_lower:
            self._handle_expand_command()
        else:
            # Custom question for ChatGPT
            self._handle_custom_question(command)
    
    def _handle_explain_command(self):
        """Handle 'explain' voice command."""
        if self.chatgpt_explainer and self.current_verse_data:
            try:
                book, reference, text = self.current_verse_data
                explanation = self.chatgpt_explainer.explain_verse(book, reference, text)
                if self.audio_manager and hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(explanation)
            except Exception as e:
                if self.debug:
                    print(f"Explanation error: {e}")
    
    def _handle_repeat_command(self):
        """Handle 'repeat' voice command."""
        if self.audio_manager and self.current_verse_data:
            try:
                book, reference, text = self.current_verse_data
                full_text = f"{reference}. {text}"
                if hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(full_text)
            except Exception as e:
                if self.debug:
                    print(f"Repeat error: {e}")
    
    def _handle_reference_command(self):
        """Handle 'reference' voice command."""
        if self.audio_manager and self.current_verse_data:
            try:
                book, reference, text = self.current_verse_data
                if hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(f"The reference is {reference}")
            except Exception as e:
                if self.debug:
                    print(f"Reference error: {e}")
    
    def _handle_mode_command(self):
        """Handle 'mode' voice command."""
        if self.audio_manager:
            try:
                mode_text = f"Current mode is {self.current_mode.replace('_', ' ')}"
                if hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(mode_text)
            except Exception as e:
                if self.debug:
                    print(f"Mode announcement error: {e}")
    
    def _handle_time_command(self):
        """Handle 'time' voice command."""
        if self.audio_manager:
            try:
                current_time = datetime.now().strftime("%I:%M %p")
                time_text = f"The current time is {current_time}"
                if hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(time_text)
            except Exception as e:
                if self.debug:
                    print(f"Time announcement error: {e}")
    
    def _handle_expand_command(self):
        """Handle 'expand' voice command to show rest of chapter."""
        if self.debug:
            print("Expand command - showing rest of chapter")
        # TODO: Implement chapter expansion functionality
        # This would show remaining verses in the current chapter
    
    def _handle_custom_question(self, question: str):
        """Handle custom questions for ChatGPT."""
        if self.chatgpt_explainer and self.current_verse_data:
            try:
                book, reference, text = self.current_verse_data
                response = self.chatgpt_explainer.answer_question(question, book, reference, text)
                if self.audio_manager and hasattr(self.audio_manager, 'speak_text'):
                    self.audio_manager.speak_text(response)
            except Exception as e:
                if self.debug:
                    print(f"Custom question error: {e}")
    
    def _get_verse_for_mode(self, target_time: datetime = None) -> tuple:
        """
        Get verse based on current mode and time.
        
        Args:
            target_time: Specific time to use. Uses current time if None.
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text)
        """
        if target_time is None:
            target_time = datetime.now()
        
        # Convert to 12-hour format
        hour = target_time.hour
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour -= 12
        
        minute = target_time.minute
        
        # Get verse based on current mode
        if self.current_mode == config.DAY_MODE:
            # Day mode: use day of year for additional randomization
            day_of_year = target_time.timetuple().tm_yday
            # Modify selection based on day (implementation can vary)
            pass
        
        # Get verse for the time
        verse_data = self.verse_selector.get_verse_for_display(hour, minute)
        
        if verse_data:
            return verse_data
        else:
            # Fallback verse
            return ("Ecclesiastes", "Ecclesiastes 3:1", 
                   "To every thing there is a season, and a time to every purpose under the heaven:")
    
    def _update_display(self, target_time: datetime = None):
        """Update the display with current verse."""
        try:
            # Get verse for current time and mode
            verse_data = self._get_verse_for_mode(target_time)
            self.current_verse_data = verse_data
            
            if verse_data:
                book_name, verse_reference, verse_text = verse_data
                
                if self.debug:
                    print(f"Displaying: {verse_reference}")
                    print(f"Text: {verse_text[:100]}...")
                
                # Get current time string
                current_time_str = target_time.strftime("%I:%M %p") if target_time else datetime.now().strftime("%I:%M %p")
                
                # Display based on current version setting
                if self.current_version == config.KJV_AMPLIFIED:
                    # Display with amplified version (side-by-side)
                    self.display.display_verse(
                        book=book_name,
                        verse_ref=verse_reference, 
                        verse_text=verse_text,
                        current_time=current_time_str,
                        mode=self.current_mode,
                        version=config.KJV_AMPLIFIED
                    )
                else:
                    # KJV only
                    self.display.display_verse(
                        book=book_name,
                        verse_ref=verse_reference,
                        verse_text=verse_text, 
                        current_time=current_time_str,
                        mode=self.current_mode,
                        version=config.KJV_ONLY
                    )
            
        except Exception as e:
            if self.debug:
                print(f"Display update error: {e}")
            # Show error message on display with proper parameters
            try:
                current_time_str = datetime.now().strftime("%I:%M %p")
                self.display.display_verse(
                    book="Error",
                    verse_ref="System Error", 
                    verse_text=f"Display update failed: {str(e)}",
                    current_time=current_time_str,
                    mode=self.current_mode,
                    version=self.current_version
                )
            except Exception as display_error:
                if self.debug:
                    print(f"Error display failed: {display_error}")
    
    def run_once(self, target_time: datetime = None):
        """Run the clock once (for testing)."""
        if self.debug:
            print("Running Bible Clock once...")
        
        self._update_display(target_time)
        
        if self.debug:
            print("Single run completed")
    
    def run(self):
        """Run the main clock loop."""
        self.running = True
        
        if self.debug:
            print("Starting Bible Clock main loop...")
        
        try:
            last_minute = -1
            
            while self.running:
                current_time = datetime.now()
                current_minute = current_time.minute
                
                # Update display when minute changes
                if current_minute != last_minute:
                    self._update_display(current_time)
                    last_minute = current_minute
                
                # Sleep for a short time to avoid excessive CPU usage
                time.sleep(1)
                
        except KeyboardInterrupt:
            if self.debug:
                print("\nKeyboard interrupt received")
        except Exception as e:
            if self.debug:
                print(f"Main loop error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the clock and cleanup resources."""
        self.running = False
        
        if self.debug:
            print("Stopping Bible Clock...")
        
        # Cleanup components with error handling
        try:
            if hasattr(self.buttons, 'cleanup'):
                self.buttons.cleanup()
        except Exception as e:
            if self.debug:
                print(f"Button cleanup error: {e}")
        
        try:
            if hasattr(self.display, 'cleanup'):
                self.display.cleanup()
        except Exception as e:
            if self.debug:
                print(f"Display cleanup error: {e}")
        
        try:
            if hasattr(self.display, 'sleep_display'):
                self.display.sleep_display()
        except Exception as e:
            if self.debug:
                print(f"Display sleep error: {e}")
        
        # Cleanup audio and voice components with error handling
        if self.voice_controller:
            try:
                if hasattr(self.voice_controller, 'stop'):
                    self.voice_controller.stop()
                elif hasattr(self.voice_controller, 'cleanup'):
                    self.voice_controller.cleanup()
                elif hasattr(self.voice_controller, 'shutdown'):
                    self.voice_controller.shutdown()
            except Exception as e:
                if self.debug:
                    print(f"Voice controller cleanup error: {e}")
        
        if self.audio_manager:
            try:
                if hasattr(self.audio_manager, 'cleanup'):
                    self.audio_manager.cleanup()
                elif hasattr(self.audio_manager, 'stop'):
                    self.audio_manager.stop()
                elif hasattr(self.audio_manager, 'shutdown'):
                    self.audio_manager.shutdown()
            except Exception as e:
                if self.debug:
                    print(f"Audio manager cleanup error: {e}")
        
        if self.debug:
            print("Bible Clock stopped")
    
    def get_status(self) -> dict:
        """Get current status of the Bible Clock."""
        return {
            'running': self.running,
            'simulate': self.simulate,
            'debug': self.debug,
            'current_mode': self.current_mode,
            'current_version': self.current_version,
            'audio_available': AUDIO_AVAILABLE and self.audio_manager is not None,
            'voice_available': VOICE_AVAILABLE and self.voice_controller is not None,
            'chatgpt_available': CHATGPT_AVAILABLE and self.chatgpt_explainer is not None,
            'current_verse': self.current_verse_data[1] if self.current_verse_data else None
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Bible Clock - Enhanced Version')
    parser.add_argument('--simulate', action='store_true', 
                       help='Run in simulation mode (no GPIO)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (for testing)')
    parser.add_argument('--time', type=str,
                       help='Specific time to display (format: "HH:MM AM/PM")')
    parser.add_argument('--test-buttons', action='store_true',
                       help='Test button functionality')
    parser.add_argument('--test-audio', action='store_true',
                       help='Test audio functionality')
    parser.add_argument('--test-voice', action='store_true',
                       help='Test voice recognition')
    parser.add_argument('--status', action='store_true',
                       help='Show status and exit')
    
    args = parser.parse_args()
    
    try:
        # Create Bible Clock instance
        clock = BibleClock(simulate=args.simulate, debug=args.debug)
        
        # Handle status request
        if args.status:
            status = clock.get_status()
            print("Bible Clock Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return 0
        
        # Handle test modes
        if args.test_buttons:
            print("Testing button functionality...")
            clock.buttons.simulate_button1_press()
            time.sleep(1)
            clock.buttons.simulate_button2_press()
            time.sleep(1)
            if hasattr(clock.buttons, 'simulate_button3_press'):
                clock.buttons.simulate_button3_press()
            return 0
        
        if args.test_audio:
            print("Testing audio functionality...")
            if clock.audio_manager:
                try:
                    if hasattr(clock.audio_manager, 'speak_text'):
                        clock.audio_manager.speak_text("Bible Clock audio test")
                    else:
                        print("Audio manager available but no speak_text method")
                except Exception as e:
                    print(f"Audio test error: {e}")
            else:
                print("Audio not available")
            return 0
        
        if args.test_voice:
            print("Testing voice recognition...")
            if clock.voice_controller:
                try:
                    print("Voice controller available - test implementation needed")
                except Exception as e:
                    print(f"Voice test error: {e}")
            else:
                print("Voice recognition not available")
            return 0
        
        # Handle specific time
        target_time = None
        if args.time:
            try:
                target_time = datetime.strptime(args.time, "%I:%M %p")
                target_time = target_time.replace(year=datetime.now().year,
                                                month=datetime.now().month,
                                                day=datetime.now().day)
            except ValueError:
                print(f"Invalid time format: {args.time}. Use format like '3:16 PM'")
                return 1
        
        # Run the clock
        if args.once:
            clock.run_once(target_time)
        else:
            clock.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    finally:
        # Ensure cleanup
        try:
            clock.stop()
        except:
            pass


if __name__ == "__main__":
    sys.exit(main())

