#!/usr/bin/env python3
"""
Bible Clock
A Raspberry Pi Bible clock that displays verses based on time or historical events.

Features:
- Mode cycling: Clock mode (time-based) ↔ Day mode (historical events)
- Version toggle: KJV only ↔ KJV + Amplified side-by-side
- Improved layout: Centered verse text, reference in bottom right
- Button controls: Button 1 (mode), Button 2 (version)
"""

import sys
import os
import time
import signal
import argparse
from datetime import datetime, date
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import config
from verse_database import VerseDatabase
from verse_selector import VerseSelector
from historical_events import HistoricalEvents
from display import DisplayManager
from buttons import ButtonManager
from time_utils import parse_12_hour_time, format_time_12_hour


class BibleClock:
    """Bible Clock with mode cycling and version toggle."""
    
    def __init__(self, simulate: bool = False, debug: bool = False):
        """
        Initialize the Bible Clock.
        
        Args:
            simulate: Run in simulation mode
            debug: Enable debug output
        """
        self.simulate = simulate
        self.debug = debug
        self.running = False
        
        # Initialize time synchronization
        from time_sync import TimeSync
        self.time_sync = TimeSync(debug=debug)
        
        # Ensure time is synchronized on startup
        if not simulate:
            if debug:
                print("Synchronizing time...")
            sync_success = self.time_sync.ensure_time_sync()
            if debug:
                if sync_success:
                    print("Time synchronization successful")
                else:
                    print("Warning: Time synchronization failed - using system time")
        
        # Initialize components
        self.verse_db = VerseDatabase()
        self.verse_selector = VerseSelector(self.verse_db)
        self.historical_events = HistoricalEvents()
        self.display = DisplayManager(simulate=simulate)
        self.buttons = ButtonManager(simulate=simulate)
        
        # Current state
        self.current_mode = config.CLOCK_MODE
        self.current_version = config.KJV_ONLY
        self.last_update_time = None
        
        # Setup button callbacks
        self.buttons.set_mode_callback(self._on_mode_change)
        self.buttons.set_version_callback(self._on_version_change)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if self.debug:
            print("Bible Clock initialized")
            print(f"Mode: {self.current_mode}")
            print(f"Version: {self.current_version}")
            print(f"Simulation: {self.simulate}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.stop()
    
    def _on_mode_change(self, new_mode: str):
        """Handle mode change from button press."""
        self.current_mode = new_mode
        if self.debug:
            print(f"Mode changed to: {new_mode}")
        
        # Immediately update display with new mode
        self._update_display()
    
    def _on_version_change(self, new_version: str):
        """Handle version change from button press."""
        self.current_version = new_version
        if self.debug:
            print(f"Version changed to: {new_version}")
        
        # Immediately update display with new version
        self._update_display()
    
    def _get_verse_for_mode(self, target_time: datetime = None) -> tuple:
        """
        Get verse based on current mode.
        
        Args:
            target_time: Time to get verse for. Uses current time if None.
            
        Returns:
            Tuple of (book, verse_ref, verse_text, description)
        """
        if target_time is None:
            target_time = datetime.now()
        
        if self.current_mode == config.CLOCK_MODE:
            # Clock mode: time-based verse selection
            hour = target_time.hour
            minute = target_time.minute
            
            # Convert to 12-hour format for verse selection
            if hour == 0:
                display_hour = 12
            elif hour > 12:
                display_hour = hour - 12
            else:
                display_hour = hour
            
            verse_info = self.verse_selector.select_verse_for_time(display_hour, minute)
            if verse_info:
                book, verse_ref, text = verse_info
                description = "Clock Mode"
                return (book, verse_ref, text, description)
            else:
                # Fallback
                return ("John", "John 3:16", 
                       "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                       "Clock Mode (Fallback)")
        
        else:  # DAY_MODE
            # Day mode: historical events-based verse selection
            month, day, year, month_name, season = self.get_current_date_info()
            
            if self.debug:
                print(f"Day mode: {month_name} {day}, {year} ({season})")
            
            # Use the historical events system with comprehensive date info
            target_date = target_time.date()
            verse_ref, description = self.historical_events.get_random_verse_for_date(target_date)
            
            # Get the verse text from database
            try:
                # Parse the verse reference
                parts = verse_ref.split()
                if len(parts) >= 2:
                    book = ' '.join(parts[:-1])
                    chapter_verse = parts[-1]
                    chapter, verse = map(int, chapter_verse.split(':'))
                    
                    verse_info = self.verse_db.get_verse(book, chapter, verse)
                    if verse_info:
                        text = verse_info['text']
                        return (book, verse_ref, text, f"Day Mode - {description}")
                    else:
                        # Try to find any verse from this book/chapter
                        verses = self.verse_db.get_verses_by_chapter(book, chapter)
                        if verses:
                            first_verse = verses[0]
                            text = first_verse['text']
                            verse_ref = f"{book} {chapter}:{first_verse['verse']}"
                            return (book, verse_ref, text, f"Day Mode - {description}")
            except:
                pass
            
            # Ultimate fallback for day mode
            return ("Psalms", "Psalms 118:24", 
                   "This is the day which the LORD hath made; we will rejoice and be glad in it.",
                   f"Day Mode - {description}")
    
    def _update_display(self, target_time: datetime = None):
        """Update the display with current verse."""
        if target_time is None:
            target_time = datetime.now()
        
        # Get verse for current mode
        book, verse_ref, verse_text, description = self._get_verse_for_mode(target_time)
        
        # Format current time
        current_time_str = format_time_12_hour(target_time.hour, target_time.minute)
        
        # Display the verse
        self.display.display_verse(
            book=book,
            verse_ref=verse_ref,
            verse_text=verse_text,
            current_time=current_time_str,
            mode=self.current_mode,
            version=self.current_version
        )
        
        if self.debug:
            print(f"Display updated: {verse_ref} ({description})")
            print(f"Mode: {self.current_mode}, Version: {self.current_version}")
    
    def run_once(self, target_time: datetime = None):
        """Run the clock once and update display."""
        if self.debug:
            print("Running Bible Clock once...")
        
        self._update_display(target_time)
        
        if self.debug:
            print("Single update completed")
    
    def run_continuous(self):
        """Run the clock continuously, updating every minute."""
        self.running = True
        
        if self.debug:
            print("Starting continuous Bible Clock...")
            print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                current_time = datetime.now()
                
                # Update display if minute has changed or first run
                if (self.last_update_time is None or 
                    current_time.minute != self.last_update_time.minute):
                    
                    self._update_display(current_time)
                    self.last_update_time = current_time
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(1)
                
        except KeyboardInterrupt:
            if self.debug:
                print("\nKeyboard interrupt received")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the clock and cleanup resources."""
        self.running = False
        
        if self.debug:
            print("Stopping Bible Clock...")
        
        # Cleanup components
        self.buttons.cleanup()
        self.display.sleep_display()
        
        if self.debug:
            print("Bible Clock stopped")
    
    def get_current_date_info(self):
        """Get current date information for day mode."""
        if hasattr(self, 'time_sync'):
            return self.time_sync.get_date_info()
        else:
            # Fallback if time_sync not available
            from datetime import datetime
            now = datetime.now()
            month = now.month
            day = now.day
            year = now.year
            month_name = now.strftime("%B")
            
            # Determine season
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Autumn"
            
            return month, day, year, month_name, season
    
    def get_status(self) -> dict:
        return {
            'running': self.running,
            'mode': self.current_mode,
            'version': self.current_version,
            'simulate': self.simulate,
            'debug': self.debug,
            'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
            'display_info': self.display.get_display_info(),
            'button_status': self.buttons.get_status(),
            'verse_stats': self.verse_selector.get_statistics(),
            'events_stats': self.historical_events.get_statistics(),
            'time_sync_status': self.time_sync.get_status() if hasattr(self, 'time_sync') else None
        }
        
        # Add current date info if available
        try:
            month, day, year, month_name, season = self.get_current_date_info()
            status['current_date_info'] = {
                'month': month,
                'day': day, 
                'year': year,
                'month_name': month_name,
                'season': season
            }
        except:
            status['current_date_info'] = None
            
        return status
    
    def simulate_button_press(self, button_number: int):
        """Simulate button press for testing."""
        if button_number == 1:
            self.buttons.simulate_button1_press()
        elif button_number == 2:
            self.buttons.simulate_button2_press()
        else:
            print(f"Invalid button number: {button_number}")


def main():
    """Main entry point for the Bible Clock."""
    parser = argparse.ArgumentParser(description='Bible Clock with mode cycling and version toggle')
    parser.add_argument('--simulate', action='store_true', 
                       help='Run in simulation mode (no GPIO)')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit (for testing)')
    parser.add_argument('--time', type=str, 
                       help='Specific time to display (e.g., "2:37 PM")')
    parser.add_argument('--mode', choices=[config.CLOCK_MODE, config.DAY_MODE],
                       help='Set initial display mode')
    parser.add_argument('--version', choices=[config.KJV_ONLY, config.KJV_AMPLIFIED],
                       help='Set initial version display')
    parser.add_argument('--status', action='store_true',
                       help='Show status information and exit')
    parser.add_argument('--test-buttons', action='store_true',
                       help='Test button functionality')
    
    args = parser.parse_args()
    
    # Create Bible Clock instance
    clock = BibleClock(simulate=args.simulate, debug=args.debug)
    
    # Set initial mode and version if specified
    if args.mode:
        clock.current_mode = args.mode
        clock.buttons.set_mode(args.mode)
    
    if args.version:
        clock.current_version = args.version
        clock.buttons.set_version(args.version)
    
    try:
        if args.status:
            # Show status and exit
            status = clock.get_status()
            print("Bible Clock Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return
        
        if args.test_buttons:
            # Test button functionality
            print("Testing button functionality...")
            print("Current mode:", clock.current_mode)
            print("Current version:", clock.current_version)
            
            print("\nSimulating Button 1 press (mode cycle)...")
            clock.simulate_button_press(1)
            print("New mode:", clock.current_mode)
            
            print("\nSimulating Button 2 press (version toggle)...")
            clock.simulate_button_press(2)
            print("New version:", clock.current_version)
            
            return
        
        if args.once:
            # Run once
            target_time = None
            if args.time:
                try:
                    hour, minute = parse_12_hour_time(args.time)
                    # Create a datetime with the parsed time
                    now = datetime.now()
                    target_time = now.replace(hour=hour if hour != 12 else 0 if 'AM' in args.time.upper() else 12, 
                                            minute=minute, second=0, microsecond=0)
                    if 'PM' in args.time.upper() and hour != 12:
                        target_time = target_time.replace(hour=target_time.hour + 12)
                except ValueError as e:
                    print(f"Error parsing time: {e}")
                    return 1
            
            clock.run_once(target_time)
            
            if args.simulate:
                print("\nPress Enter to exit...")
                input()
        else:
            # Run continuously
            clock.run_continuous()
    
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        clock.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

