"""
Bible verse database module for the Bible Clock.
Loads and queries KJV JSON Bible data.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
import config


class VerseDatabase:
    """Handles loading and querying of KJV Bible data."""
    
    def __init__(self, data_path: str = None):
        """
        Initialize the verse database.
        
        Args:
            data_path: Path to the KJV JSON file. Uses default if None.
        """
        self.data_path = data_path or config.BIBLE_DATA_PATH
        self.verses = {}
        self.book_structure = {}
        self._load_bible_data()
    
    def _load_bible_data(self):
        """Load Bible data from JSON file and build book structure."""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.verses = json.load(f)
            
            # Build book structure for efficient chapter/verse lookup
            self._build_book_structure()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Bible data file not found: {self.data_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Bible data file: {e}")
    
    def _build_book_structure(self):
        """Build a structure mapping books to their available chapters and verses."""
        self.book_structure = {}
        
        for verse_ref, verse_text in self.verses.items():
            # Parse verse reference like "Genesis 1:1"
            parts = verse_ref.split(' ')
            if len(parts) < 2:
                continue
                
            # Handle multi-word book names
            chapter_verse = parts[-1]
            book_name = ' '.join(parts[:-1])
            
            if ':' not in chapter_verse:
                continue
                
            try:
                chapter, verse = chapter_verse.split(':')
                chapter = int(chapter)
                verse = int(verse)
                
                if book_name not in self.book_structure:
                    self.book_structure[book_name] = {}
                
                if chapter not in self.book_structure[book_name]:
                    self.book_structure[book_name][chapter] = set()
                
                self.book_structure[book_name][chapter].add(verse)
                
            except ValueError:
                # Skip malformed references
                continue
    
    def get_books_with_chapter_verse(self, chapter: int, verse: int) -> List[str]:
        """
        Get all books that have the specified chapter and verse.
        
        Args:
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            List of book names that contain the specified chapter:verse
        """
        matching_books = []
        
        for book_name, chapters in self.book_structure.items():
            if chapter in chapters and verse in chapters[chapter]:
                matching_books.append(book_name)
        
        return matching_books
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """
        Get a specific verse text.
        
        Args:
            book: Book name
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Verse text or None if not found
        """
        verse_ref = f"{book} {chapter}:{verse}"
        return self.verses.get(verse_ref)
    
    def get_random_verse_for_time(self, chapter: int, verse: int) -> Optional[Tuple[str, str, str]]:
        """
        Get a random verse that matches the given chapter and verse numbers.
        
        Args:
            chapter: Chapter number (from hour)
            verse: Verse number (from minute)
            
        Returns:
            Tuple of (book_name, verse_reference, verse_text) or None if no match
        """
        matching_books = self.get_books_with_chapter_verse(chapter, verse)
        
        if not matching_books:
            return None
        
        # Select a random book from those that have this chapter:verse
        selected_book = random.choice(matching_books)
        verse_ref = f"{selected_book} {chapter}:{verse}"
        verse_text = self.verses.get(verse_ref)
        
        if verse_text:
            return selected_book, verse_ref, verse_text
        
        return None
    
    def get_book_names(self) -> List[str]:
        """Get all available book names."""
        return list(self.book_structure.keys())
    
    def get_chapter_count(self, book: str) -> int:
        """Get the number of chapters in a book."""
        if book in self.book_structure:
            return max(self.book_structure[book].keys()) if self.book_structure[book] else 0
        return 0
    
    def get_verse_count(self, book: str, chapter: int) -> int:
        """Get the number of verses in a specific chapter."""
        if book in self.book_structure and chapter in self.book_structure[book]:
            return max(self.book_structure[book][chapter]) if self.book_structure[book][chapter] else 0
        return 0

