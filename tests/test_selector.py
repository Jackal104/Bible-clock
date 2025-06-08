"""
Unit tests for verse selection functionality.
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from verse_selector import VerseSelector
from verse_database import VerseDatabase


class TestVerseSelector(unittest.TestCase):
    """Test cases for VerseSelector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.selector = VerseSelector()
    
    def test_verse_selector_initialization(self):
        """Test that VerseSelector initializes correctly."""
        self.assertIsNotNone(self.selector)
        self.assertIsNotNone(self.selector.database)
    
    def test_select_verse_for_time(self):
        """Test verse selection for specific times."""
        # Test with a time that should have verses
        result = self.selector.select_verse_for_time(2, 37)
        if result:
            book, verse_ref, verse_text = result
            self.assertIsInstance(book, str)
            self.assertIsInstance(verse_ref, str)
            self.assertIsInstance(verse_text, str)
            self.assertIn("2:37", verse_ref)
    
    def test_get_verse_for_display_with_fallback(self):
        """Test that get_verse_for_display always returns a result."""
        # Test with various times
        test_times = [(1, 1), (2, 37), (12, 59), (6, 30)]
        
        for hour, minute in test_times:
            result = self.selector.get_verse_for_display(hour, minute)
            self.assertIsNotNone(result)
            
            book, verse_ref, verse_text = result
            self.assertIsInstance(book, str)
            self.assertIsInstance(verse_ref, str)
            self.assertIsInstance(verse_text, str)
            self.assertTrue(len(book) > 0)
            self.assertTrue(len(verse_ref) > 0)
            self.assertTrue(len(verse_text) > 0)
    
    def test_fallback_verse(self):
        """Test fallback verse functionality."""
        # Test with an impossible time (should trigger fallback)
        result = self.selector.get_fallback_verse(99, 99)
        self.assertIsNotNone(result)
        
        book, verse_ref, verse_text = result
        self.assertIsInstance(book, str)
        self.assertIsInstance(verse_ref, str)
        self.assertIsInstance(verse_text, str)
    
    def test_get_statistics(self):
        """Test statistics generation."""
        stats = self.selector.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_books', stats)
        self.assertIn('available_times', stats)
        self.assertIn('total_possible_times', stats)
        self.assertIn('coverage_percentage', stats)
        
        # Check that values are reasonable
        self.assertGreater(stats['total_books'], 0)
        self.assertGreater(stats['available_times'], 0)
        self.assertEqual(stats['total_possible_times'], 720)  # 12 hours * 60 minutes
        self.assertGreaterEqual(stats['coverage_percentage'], 0)
        self.assertLessEqual(stats['coverage_percentage'], 100)
    
    def test_get_available_times(self):
        """Test getting available times."""
        available_times = self.selector.get_available_times()
        
        self.assertIsInstance(available_times, list)
        self.assertGreater(len(available_times), 0)
        
        # Check that each time is a valid tuple
        for hour, minute in available_times[:10]:  # Check first 10
            self.assertIsInstance(hour, int)
            self.assertIsInstance(minute, int)
            self.assertGreaterEqual(hour, 1)
            self.assertLessEqual(hour, 12)
            self.assertGreaterEqual(minute, 0)
            self.assertLessEqual(minute, 59)


class TestVerseDatabase(unittest.TestCase):
    """Test cases for VerseDatabase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.database = VerseDatabase()
    
    def test_database_initialization(self):
        """Test that VerseDatabase initializes correctly."""
        self.assertIsNotNone(self.database)
        self.assertIsInstance(self.database.verses, dict)
        self.assertGreater(len(self.database.verses), 0)
    
    def test_get_books_with_chapter_verse(self):
        """Test getting books with specific chapter and verse."""
        # Test with John 3:16 (should exist)
        books = self.database.get_books_with_chapter_verse(3, 16)
        self.assertIsInstance(books, list)
        self.assertIn("John", books)
        
        # Test with a common chapter:verse combination
        books = self.database.get_books_with_chapter_verse(1, 1)
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)
    
    def test_get_verse(self):
        """Test getting specific verses."""
        # Test John 3:16
        verse = self.database.get_verse("John", 3, 16)
        self.assertIsNotNone(verse)
        self.assertIsInstance(verse, str)
        self.assertIn("God", verse)
        self.assertIn("world", verse)
    
    def test_get_random_verse_for_time(self):
        """Test getting random verses for specific times."""
        # Test with a time that should have verses
        result = self.database.get_random_verse_for_time(1, 1)
        if result:
            book, verse_ref, verse_text = result
            self.assertIsInstance(book, str)
            self.assertIsInstance(verse_ref, str)
            self.assertIsInstance(verse_text, str)
            self.assertIn("1:1", verse_ref)
    
    def test_get_book_names(self):
        """Test getting all book names."""
        books = self.database.get_book_names()
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)
        
        # Check for some expected books
        expected_books = ["Genesis", "Exodus", "Matthew", "John", "Revelation"]
        for book in expected_books:
            self.assertIn(book, books)
    
    def test_get_chapter_count(self):
        """Test getting chapter counts for books."""
        # Test Genesis (should have many chapters)
        genesis_chapters = self.database.get_chapter_count("Genesis")
        self.assertGreater(genesis_chapters, 40)
        
        # Test a book that doesn't exist
        nonexistent_chapters = self.database.get_chapter_count("NonexistentBook")
        self.assertEqual(nonexistent_chapters, 0)
    
    def test_get_verse_count(self):
        """Test getting verse counts for chapters."""
        # Test Genesis 1 (should have many verses)
        genesis_1_verses = self.database.get_verse_count("Genesis", 1)
        self.assertGreater(genesis_1_verses, 20)
        
        # Test a chapter that doesn't exist
        nonexistent_verses = self.database.get_verse_count("Genesis", 999)
        self.assertEqual(nonexistent_verses, 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

