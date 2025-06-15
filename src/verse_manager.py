"""
Enhanced Verse Manager

This module handles verse selection logic, time-based verse matching,
and verse formatting for display.
"""

import logging
import random
from datetime import datetime, time
from typing import Optional, Dict, Any, List, Tuple
from bible_api import BibleAPI

class VerseManager:
    """Enhanced verse manager with intelligent verse selection"""
    
    def __init__(self, bible_api: BibleAPI):
        self.bible_api = bible_api
        self.logger = logging.getLogger(__name__)
        
        # Special time mappings for significant verses
        self.special_times = {
            (3, 16): ["John"],  # 3:16 - most famous verse
            (23, 1): ["Psalm"],  # 23:1 - The Lord is my shepherd
            (1, 1): ["Genesis", "John"],  # 1:1 - In the beginning
            (12, 0): ["Ecclesiastes"],  # 12:00 - Remember your Creator
            (6, 0): ["Psalm"],  # 6:00 AM - Morning prayer
            (21, 0): ["Psalm"],  # 9:00 PM - Evening prayer
        }
        
        # Book preferences for different times of day
        self.time_preferences = {
            'morning': ["Psalm", "Proverbs", "Ecclesiastes"],
            'afternoon': ["Matthew", "Mark", "Luke", "John"],
            'evening': ["Psalm", "Romans", "Ephesians"],
            'night': ["Psalm", "1 Peter", "Philippians"]
        }
    
    def get_verse_for_current_time(self) -> Optional[Dict[str, Any]]:
        """Get verse for current time"""
        now = datetime.now()
        return self.get_verse_for_time(now.hour, now.minute)
    
    def get_verse_for_time(self, hour: int, minute: int) -> Optional[Dict[str, Any]]:
        """
        Get verse for specific time with intelligent selection
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            Dict containing verse data or None if not found
        """
        self.logger.info(f"Getting verse for {hour:02d}:{minute:02d}")
        
        # Convert to 12-hour format for verse matching
        display_hour = self._convert_to_12_hour(hour)
        
        # Check for special time mappings first
        verse_data = self._get_special_verse(display_hour, minute)
        if verse_data:
            return verse_data
        
        # Get time-appropriate books
        preferred_books = self._get_time_appropriate_books(hour)
        
        # Try to find verse with preferred books first
        verse_data = self._find_verse_with_books(display_hour, minute, preferred_books)
        if verse_data:
            return verse_data
        
        # Fall back to any available verse
        return self.bible_api.get_random_verse_for_time(hour, minute)
    
    def _convert_to_12_hour(self, hour: int) -> int:
        """Convert 24-hour to 12-hour format"""
        if hour == 0:
            return 12
        elif hour <= 12:
            return hour
        else:
            return hour - 12
    
    def _get_special_verse(self, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Get special verse for significant times"""
        time_key = (chapter, verse)
        
        if time_key in self.special_times:
            preferred_books = self.special_times[time_key]
            
            for book in preferred_books:
                verse_data = self.bible_api.get_verse(book, chapter, verse)
                if verse_data:
                    verse_data['special'] = True
                    self.logger.info(f"Found special verse: {book} {chapter}:{verse}")
                    return verse_data
        
        return None
    
    def _get_time_appropriate_books(self, hour: int) -> List[str]:
        """Get books appropriate for time of day"""
        if 5 <= hour < 12:
            time_period = 'morning'
        elif 12 <= hour < 17:
            time_period = 'afternoon'
        elif 17 <= hour < 21:
            time_period = 'evening'
        else:
            time_period = 'night'
        
        return self.time_preferences.get(time_period, [])
    
    def _find_verse_with_books(self, chapter: int, verse: int, 
                              preferred_books: List[str]) -> Optional[Dict[str, Any]]:
        """Find verse using preferred books"""
        # Shuffle to add randomness
        books_to_try = preferred_books.copy()
        random.shuffle(books_to_try)
        
        for book in books_to_try:
            verse_data = self.bible_api.get_verse(book, chapter, verse)
            if verse_data and verse_data.get('text'):
                self.logger.debug(f"Found verse with preferred book: {book} {chapter}:{verse}")
                return verse_data
        
        return None
    
    def format_verse_for_display(self, verse_data: Dict[str, Any], 
                                current_time: Optional[datetime] = None) -> Dict[str, str]:
        """
        Format verse data for display
        
        Args:
            verse_data: Verse data from API
            current_time: Current time for display
            
        Returns:
            Dict with formatted text components
        """
        if not current_time:
            current_time = datetime.now()
        
        # Extract verse components
        reference = verse_data.get('reference', 'Unknown')
        text = verse_data.get('text', '')
        translation = verse_data.get('translation_name', 'KJV')
        
        # Clean up text
        text = self._clean_verse_text(text)
        
        # Format time
        time_str = current_time.strftime("%I:%M %p")
        date_str = current_time.strftime("%A, %B %d, %Y")
        
        # Create display components
        return {
            'time': time_str,
            'date': date_str,
            'reference': reference,
            'text': text,
            'translation': translation,
            'source': verse_data.get('source', 'unknown'),
            'is_special': verse_data.get('special', False)
        }
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean and format verse text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Ensure proper punctuation
        if not text.endswith(('.', '!', '?', ':')):
            text += '.'
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def get_verse_statistics(self) -> Dict[str, Any]:
        """Get statistics about verse retrieval"""
        cache_stats = self.bible_api.get_cache_stats()
        
        return {
            'cache_stats': cache_stats,
            'special_times_count': len(self.special_times),
            'time_preferences_count': len(self.time_preferences)
        }
    
    def validate_verse_availability(self, hour: int, minute: int) -> Dict[str, Any]:
        """
        Validate that verses are available for a specific time
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            Dict with validation results
        """
        display_hour = self._convert_to_12_hour(hour)
        
        validation = {
            'time': f"{hour:02d}:{minute:02d}",
            'display_time': f"{display_hour}:{minute:02d}",
            'has_special_verse': (display_hour, minute) in self.special_times,
            'preferred_books': self._get_time_appropriate_books(hour),
            'verse_found': False,
            'verse_source': None
        }
        
        # Try to get verse
        verse_data = self.get_verse_for_time(hour, minute)
        if verse_data:
            validation['verse_found'] = True
            validation['verse_source'] = verse_data.get('source', 'unknown')
            validation['reference'] = verse_data.get('reference', 'Unknown')
        
        return validation


class VerseScheduler:
    """Handles verse scheduling and rotation"""
    
    def __init__(self, verse_manager: VerseManager):
        self.verse_manager = verse_manager
        self.logger = logging.getLogger(__name__)
        self.last_update_time = None
        self.current_verse = None
    
    def should_update_verse(self, current_time: datetime) -> bool:
        """Check if verse should be updated"""
        if not self.last_update_time:
            return True
        
        # Update if minute has changed
        if (current_time.hour != self.last_update_time.hour or 
            current_time.minute != self.last_update_time.minute):
            return True
        
        return False
    
    def get_current_verse(self, force_update: bool = False) -> Optional[Dict[str, Any]]:
        """Get current verse, updating if necessary"""
        current_time = datetime.now()
        
        if force_update or self.should_update_verse(current_time):
            self.logger.info("Updating verse for new time")
            verse_data = self.verse_manager.get_verse_for_current_time()
            
            if verse_data:
                self.current_verse = self.verse_manager.format_verse_for_display(
                    verse_data, current_time
                )
                self.last_update_time = current_time
                self.logger.info(f"Updated to verse: {self.current_verse.get('reference', 'Unknown')}")
            else:
                self.logger.warning("No verse found for current time")
        
        return self.current_verse
    
    def get_next_update_time(self) -> Optional[datetime]:
        """Get the time when the next update should occur"""
        if not self.last_update_time:
            return None
        
        # Next update is at the next minute
        next_minute = self.last_update_time.replace(second=0, microsecond=0)
        next_minute = next_minute.replace(minute=next_minute.minute + 1)
        
        # Handle hour rollover
        if next_minute.minute == 60:
            next_minute = next_minute.replace(hour=next_minute.hour + 1, minute=0)
        
        # Handle day rollover
        if next_minute.hour == 24:
            next_minute = next_minute.replace(day=next_minute.day + 1, hour=0)
        
        return next_minute

