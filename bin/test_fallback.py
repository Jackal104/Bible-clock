#!/usr/bin/env python3
"""
Test Bible Clock with Fallback Data

This script tests the Bible Clock using only fallback data to avoid API rate limits.
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
from bible_api import BibleAPI
from verse_manager import VerseManager
from display import display_manager

def test_fallback_verses():
    """Test with fallback verses only"""
    print("=== Testing Bible Clock with Fallback Data ===")
    
    # Initialize components
    bible_api = BibleAPI(fallback_enabled=True)
    verse_manager = VerseManager(bible_api)
    
    # Test specific times with fallback data
    test_times = [
        (3, 16),   # John 3:16
        (23, 1),   # Psalm 23:1
        (8, 28),   # Romans 8:28
        (4, 13),   # Philippians 4:13
        (1, 1),    # Genesis 1:1
    ]
    
    for hour, minute in test_times:
        print(f"\nTesting time {hour:02d}:{minute:02d}")
        
        # Get verse using fallback
        reference = None
        for book in ["John", "Psalm", "Romans", "Philippians", "Genesis"]:
            verse_data = bible_api._get_from_fallback(book, hour if hour <= 12 else hour - 12, minute)
            if verse_data:
                reference = verse_data['reference']
                text = verse_data['text'][:50] + "..." if len(verse_data['text']) > 50 else verse_data['text']
                print(f"  Found: {reference}")
                print(f"  Text: {text}")
                
                # Test display
                formatted_verse = verse_manager.format_verse_for_display(verse_data)
                success = display_manager.display_verse(formatted_verse)
                print(f"  Display: {'✓' if success else '✗'}")
                break
        
        if not reference:
            print(f"  No fallback verse found for {hour:02d}:{minute:02d}")
    
    print(f"\n=== Test Complete ===")
    print(f"Generated images saved to /tmp/bible_clock_display_*.png")

if __name__ == "__main__":
    test_fallback_verses()

