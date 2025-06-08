"""
Unit tests for display simulation functionality.
"""

import unittest
import sys
import os
import tempfile
from PIL import Image

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from display import DisplayManager
import config


class TestDisplaySimulation(unittest.TestCase):
    """Test cases for display simulation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Force simulation mode for testing
        self.display = DisplayManager(simulate=True)
    
    def test_display_initialization(self):
        """Test that DisplayManager initializes correctly in simulation mode."""
        self.assertIsNotNone(self.display)
        self.assertTrue(self.display.simulate)
        self.assertEqual(self.display.width, config.DISPLAY_WIDTH)
        self.assertEqual(self.display.height, config.DISPLAY_HEIGHT)
    
    def test_font_loading(self):
        """Test that fonts load correctly."""
        self.assertIsNotNone(self.display.font)
        self.assertIsNotNone(self.display.title_font)
    
    def test_create_verse_image(self):
        """Test creating a verse image."""
        book = "John"
        verse_ref = "John 3:16"
        verse_text = "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."
        current_time = "3:16 PM"
        
        image = self.display.create_verse_image(book, verse_ref, verse_text, current_time)
        
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (self.display.width, self.display.height))
        self.assertEqual(image.mode, 'RGB')
    
    def test_clean_verse_text(self):
        """Test verse text cleaning."""
        # Test with formatting markers
        dirty_text = "# For God so loved the world, [that] he gave his only begotten Son."
        clean_text = self.display._clean_verse_text(dirty_text)
        
        self.assertNotIn('#', clean_text)
        self.assertNotIn('[', clean_text)
        self.assertNotIn(']', clean_text)
        self.assertIn('For God so loved the world', clean_text)
        self.assertIn('that', clean_text)
    
    def test_display_verse(self):
        """Test displaying a verse."""
        book = "Psalms"
        verse_ref = "Psalms 23:1"
        verse_text = "The LORD [is] my shepherd; I shall not want."
        current_time = "11:01 AM"
        
        output_path = self.display.display_verse(book, verse_ref, verse_text, current_time)
        
        # Should return a path in simulation mode
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))
        
        # Check that the image was created
        image = Image.open(output_path)
        self.assertEqual(image.size, (self.display.width, self.display.height))
    
    def test_get_display_info(self):
        """Test getting display information."""
        info = self.display.get_display_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('simulate', info)
        self.assertIn('font_size', info)
        
        self.assertEqual(info['width'], config.DISPLAY_WIDTH)
        self.assertEqual(info['height'], config.DISPLAY_HEIGHT)
        self.assertTrue(info['simulate'])
    
    def test_clear_display(self):
        """Test clearing the display."""
        # Should not raise an exception in simulation mode
        try:
            self.display.clear_display()
        except Exception as e:
            self.fail(f"clear_display() raised an exception: {e}")
    
    def test_sleep_display(self):
        """Test putting display to sleep."""
        # Should not raise an exception in simulation mode
        try:
            self.display.sleep_display()
        except Exception as e:
            self.fail(f"sleep_display() raised an exception: {e}")
    
    def test_multiple_verse_displays(self):
        """Test displaying multiple verses."""
        verses = [
            ("Genesis", "Genesis 1:1", "In the beginning God created the heaven and the earth.", "1:01 AM"),
            ("John", "John 3:16", "For God so loved the world...", "3:16 PM"),
            ("Psalms", "Psalms 23:1", "The LORD is my shepherd; I shall not want.", "11:01 PM")
        ]
        
        for book, verse_ref, verse_text, current_time in verses:
            with self.subTest(verse_ref=verse_ref):
                output_path = self.display.display_verse(book, verse_ref, verse_text, current_time)
                self.assertIsNotNone(output_path)
                self.assertTrue(os.path.exists(output_path))
    
    def test_long_verse_text(self):
        """Test displaying a very long verse."""
        book = "Esther"
        verse_ref = "Esther 8:9"
        # This is a very long verse
        verse_text = ("Then were the king's scribes called at that time in the third month, "
                     "that is, the month Sivan, on the three and twentieth day thereof; "
                     "and it was written according to all that Mordecai commanded unto the Jews, "
                     "and to the lieutenants, and the deputies and rulers of the provinces "
                     "which are from India unto Ethiopia, an hundred twenty and seven provinces, "
                     "unto every province according to the writing thereof, and unto every people "
                     "after their language, and to the Jews according to their writing, "
                     "and according to their language.")
        current_time = "8:09 AM"
        
        # Should handle long text without errors
        output_path = self.display.display_verse(book, verse_ref, verse_text, current_time)
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))
    
    def test_special_characters_in_verse(self):
        """Test displaying verses with special characters."""
        book = "Matthew"
        verse_ref = "Matthew 5:3"
        verse_text = "Blessed [are] the poor in spirit: for theirs is the kingdom of heaven."
        current_time = "5:03 AM"
        
        output_path = self.display.display_verse(book, verse_ref, verse_text, current_time)
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

