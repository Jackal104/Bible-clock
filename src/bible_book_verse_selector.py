"""
Bible Book Verse Selector - Enhanced with Random Book Summaries
Handles verse selection and random book summaries for :00 minutes
"""

import random
from typing import Optional, Tuple
from verse_database import VerseDatabase
from bible_book_summary import BibleBookSummaryProvider


class BibleBookVerseSelector:
    """Handles selection of Bible verses and random book summaries based on time."""
    
    def __init__(self, database: VerseDatabase = None):
        """
        Initialize the Bible book verse selector.
        
        Args:
            database: VerseDatabase instance. Creates new one if None.
        """
        self.database = database or VerseDatabase()
        self.book_summary = BibleBookSummaryProvider()
    
    def select_verse_for_time(self, hour: int, minute: int) -> Optional[Tuple[str, str, str]]:
        """
        Select a verse or book summary based on the current time.
        
        Args:
            hour: Hour (1-12) representing the chapter
            minute: Minute (0-59) representing the verse
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text) or None if no match
        """
        # Special handling for :00 minutes - show random book summary
        if minute == 0:
            return self._get_random_book_summary_for_time(hour)
        
        # Use hour as chapter and minute as verse for regular verses
        chapter = hour
        verse = minute
        
        return self.database.get_random_verse_for_time(chapter, verse)
    
    def _get_random_book_summary_for_time(self, hour: int) -> Tuple[str, str, str]:
        """
        Get a random book summary for :00 minute displays.
        
        Args:
            hour: Hour (1-12) representing the chapter
            
        Returns:
            Tuple of (book_name, verse_reference, summary_text)
        """
        # Get a completely random book summary from all 66 Bible books
        book_name, reference, summary_text = self.book_summary.get_random_book_summary()
        
        # Add time context to the reference
        reference_with_time = f"{reference} ({hour}:00)"
        
        return book_name, reference_with_time, summary_text
    
    def get_fallback_verse(self, hour: int, minute: int) -> Tuple[str, str, str]:
        """
        Get a fallback verse when no exact match is found.
        
        This method tries to find alternative verses by:
        1. For :00 minutes, always return a random book summary
        2. For other minutes, reduce verse number until a match is found
        3. If still no match, use a well-known verse
        
        Args:
            hour: Hour (1-12)
            minute: Minute (0-59)
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text)
        """
        # Handle :00 minutes with random book summary
        if minute == 0:
            return self._get_random_book_summary_for_time(hour)
        
        chapter = hour
        verse = minute
        
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
        Get a verse or book summary for display, with fallback handling.
        
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
        Get all available time combinations (hour:minute) that have verses or summaries.
        
        Returns:
            List of tuples (hour, minute) for which verses or summaries exist
        """
        available_times = []
        
        # Check all possible hour:minute combinations
        for hour in range(1, 13):  # 1-12 hours
            for minute in range(0, 60):  # 0-59 minutes
                if minute == 0:
                    # :00 minutes always have book summaries (all 66 books available)
                    available_times.append((hour, minute))
                else:
                    # Check if verse exists
                    if self.database.get_books_with_chapter_verse(hour, minute):
                        available_times.append((hour, minute))
        
        return available_times
    
    def get_statistics(self) -> dict:
        """
        Get statistics about verse and book summary availability.
        
        Returns:
            Dictionary with statistics
        """
        total_books = len(self.database.get_book_names())
        available_times = self.get_available_times()
        total_possible_times = 12 * 60  # 12 hours * 60 minutes
        
        # Count :00 minutes (always available with book summaries)
        book_summary_times = 12  # One for each hour
        
        # Count regular verse times
        verse_times = len([t for t in available_times if t[1] != 0])
        
        # Get book summary statistics
        summary_stats = self.book_summary.get_statistics()
        
        return {
            'total_books_in_database': total_books,
            'available_times': len(available_times),
            'total_possible_times': total_possible_times,
            'coverage_percentage': (len(available_times) / total_possible_times) * 100,
            'book_summary_times': book_summary_times,
            'verse_times': verse_times,
            'bible_book_summaries': summary_stats['total_books'],
            'old_testament_books': summary_stats['old_testament_books'],
            'new_testament_books': summary_stats['new_testament_books']
        }

