"""
Verse selector module for the Bible Clock.
Finds random book with valid chapter:verse combinations.
"""

import random
from typing import Optional, Tuple
from verse_database import VerseDatabase


class VerseSelector:
    """Handles selection of Bible verses based on time."""
    
    def __init__(self, database: VerseDatabase = None):
        """
        Initialize the verse selector.
        
        Args:
            database: VerseDatabase instance. Creates new one if None.
        """
        self.database = database or VerseDatabase()
    
    def select_verse_for_time(self, hour: int, minute: int) -> Optional[Tuple[str, str, str]]:
        """
        Select a verse based on the current time.
        
        Args:
            hour: Hour (1-12) representing the chapter
            minute: Minute (0-59) representing the verse
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text) or None if no match
        """
        # Use hour as chapter and minute as verse
        chapter = hour
        verse = minute
        
        # Handle special case where minute is 0 (should be verse 1 minimum)
        if verse == 0:
            verse = 1
        
        return self.database.get_random_verse_for_time(chapter, verse)
    
    def get_fallback_verse(self, hour: int, minute: int) -> Tuple[str, str, str]:
        """
        Get a fallback verse when no exact match is found.
        
        This method tries to find alternative verses by:
        1. Reducing the verse number until a match is found
        2. If still no match, use a well-known verse
        
        Args:
            hour: Hour (1-12)
            minute: Minute (0-59)
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text)
        """
        chapter = hour
        verse = minute if minute > 0 else 1
        
        # Try reducing verse number until we find a match
        while verse > 0:
            result = self.database.get_random_verse_for_time(chapter, verse)
            if result:
                return result
            verse -= 1
        
        # If still no match, try reducing chapter
        chapter = hour
        while chapter > 0:
            verse = 1  # Start with verse 1
            result = self.database.get_random_verse_for_time(chapter, verse)
            if result:
                return result
            chapter -= 1
        
        # Ultimate fallback - John 3:16 (most famous verse)
        fallback_verse = self.database.get_verse("John", 3, 16)
        if fallback_verse:
            return "John", "John 3:16", fallback_verse
        
        # If even John 3:16 is not available, return a generic message
        return "Bible", f"Time {hour}:{minute:02d}", "For God so loved the world..."
    
    def get_verse_for_display(self, hour: int, minute: int) -> Tuple[str, str, str]:
        """
        Get a verse for display, with fallback handling.
        
        Args:
            hour: Hour (1-12)
            minute: Minute (0-59)
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text)
        """
        # Try to get exact match first
        result = self.select_verse_for_time(hour, minute)
        
        if result:
            return result
        else:
            # Use fallback logic
            return self.get_fallback_verse(hour, minute)
    
    def get_available_times(self) -> list:
        """
        Get all available time combinations (hour:minute) that have verses.
        
        Returns:
            List of tuples (hour, minute) for which verses exist
        """
        available_times = []
        
        # Check all possible hour:minute combinations
        for hour in range(1, 13):  # 1-12 hours
            for minute in range(0, 60):  # 0-59 minutes
                verse = minute if minute > 0 else 1
                if self.database.get_books_with_chapter_verse(hour, verse):
                    available_times.append((hour, minute))
        
        return available_times
    
    def get_statistics(self) -> dict:
        """
        Get statistics about verse availability.
        
        Returns:
            Dictionary with statistics
        """
        total_books = len(self.database.get_book_names())
        available_times = self.get_available_times()
        total_possible_times = 12 * 60  # 12 hours * 60 minutes
        
        return {
            'total_books': total_books,
            'available_times': len(available_times),
            'total_possible_times': total_possible_times,
            'coverage_percentage': (len(available_times) / total_possible_times) * 100
        }

