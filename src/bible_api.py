"""
Enhanced Bible API Interface

This module provides a robust interface to Bible APIs with fallback support,
caching, and error handling.
"""

import requests
import json
import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
import random

class BibleAPI:
    """Enhanced Bible API interface with fallback and caching"""
    
    def __init__(self, api_url: str = "https://bible-api.com", 
                 version: str = "kjv", fallback_enabled: bool = True):
        self.api_url = api_url.rstrip('/')
        self.version = version
        self.fallback_enabled = fallback_enabled
        self.logger = logging.getLogger(__name__)
        
        # Cache for API responses
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
        
        # Load fallback data
        self.fallback_verses = self._load_fallback_verses()
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Bible-Clock/1.0',
            'Accept': 'application/json'
        })
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific Bible verse
        
        Args:
            book: Book name (e.g., "John", "Genesis")
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Dict containing verse data or None if not found
        """
        reference = f"{book} {chapter}:{verse}"
        
        # Check cache first
        cached_verse = self._get_from_cache(reference)
        if cached_verse:
            self.logger.debug(f"Retrieved from cache: {reference}")
            return cached_verse
        
        # Try API
        try:
            verse_data = self._fetch_from_api(reference)
            if verse_data:
                self._add_to_cache(reference, verse_data)
                return verse_data
        except Exception as e:
            self.logger.warning(f"API request failed for {reference}: {e}")
        
        # Fallback to local data
        if self.fallback_enabled:
            return self._get_from_fallback(book, chapter, verse)
        
        return None
    
    def get_random_verse_for_time(self, hour: int, minute: int) -> Optional[Dict[str, Any]]:
        """
        Get a random verse where chapter:verse matches hour:minute
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            Dict containing verse data or None if not found
        """
        # Convert 24-hour to 12-hour for verse matching
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
            
        # Find books that have the required chapter
        suitable_books = self._find_books_with_chapter(display_hour)
        
        if not suitable_books:
            self.logger.warning(f"No books found with chapter {display_hour}")
            return self._get_fallback_verse_for_time(display_hour, minute)
        
        # Try each book until we find a verse
        random.shuffle(suitable_books)
        
        for book in suitable_books:
            verse_data = self.get_verse(book, display_hour, minute)
            if verse_data and verse_data.get('text'):
                return verse_data
        
        # If no exact match, try nearby verses
        return self._get_nearby_verse(suitable_books[0], display_hour, minute)
    
    def _fetch_from_api(self, reference: str) -> Optional[Dict[str, Any]]:
        """Fetch verse from API"""
        try:
            # Format reference for API
            formatted_ref = reference.replace(' ', '%20')
            url = f"{self.api_url}/{formatted_ref}"
            
            self.logger.debug(f"Fetching from API: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response
            if 'text' in data and data['text']:
                return {
                    'reference': data.get('reference', reference),
                    'text': data['text'].strip(),
                    'translation_name': data.get('translation_name', self.version.upper()),
                    'source': 'api',
                    'timestamp': time.time()
                }
            else:
                self.logger.warning(f"Empty or invalid response for {reference}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching {reference}: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error for {reference}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {reference}: {e}")
            raise
    
    def _get_from_cache(self, reference: str) -> Optional[Dict[str, Any]]:
        """Get verse from cache if not expired"""
        if reference in self.cache:
            cached_data = self.cache[reference]
            if time.time() - cached_data['timestamp'] < self.cache_timeout:
                return cached_data
            else:
                # Remove expired entry
                del self.cache[reference]
        return None
    
    def _add_to_cache(self, reference: str, verse_data: Dict[str, Any]):
        """Add verse to cache"""
        self.cache[reference] = verse_data
        
        # Limit cache size
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_ref = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_ref]
    
    def _load_fallback_verses(self) -> Dict[str, Any]:
        """Load fallback verses from local file"""
        fallback_file = Path("data/fallback_verses.json")
        
        if fallback_file.exists():
            try:
                with open(fallback_file, 'r') as f:
                    data = json.load(f)
                    self.logger.info(f"Loaded {len(data)} fallback verses")
                    return data
            except Exception as e:
                self.logger.error(f"Error loading fallback verses: {e}")
        
        # Return minimal fallback data
        return self._get_minimal_fallback()
    
    def _get_minimal_fallback(self) -> Dict[str, Any]:
        """Get minimal fallback verses for common times"""
        return {
            "John 3:16": {
                "reference": "John 3:16",
                "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
                "translation_name": "KJV",
                "source": "fallback"
            },
            "Psalm 23:1": {
                "reference": "Psalm 23:1",
                "text": "The LORD is my shepherd; I shall not want.",
                "translation_name": "KJV",
                "source": "fallback"
            },
            "Romans 8:28": {
                "reference": "Romans 8:28",
                "text": "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.",
                "translation_name": "KJV",
                "source": "fallback"
            }
        }
    
    def _get_from_fallback(self, book: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Get verse from fallback data"""
        reference = f"{book} {chapter}:{verse}"
        
        if reference in self.fallback_verses:
            verse_data = self.fallback_verses[reference].copy()
            verse_data['source'] = 'fallback'
            verse_data['timestamp'] = time.time()
            return verse_data
        
        return None
    
    def _find_books_with_chapter(self, chapter: int) -> List[str]:
        """Find Bible books that have the specified chapter"""
        # Common books with many chapters
        books_with_many_chapters = [
            "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
            "Joshua", "Judges", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
            "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Job",
            "Psalms", "Proverbs", "Ecclesiastes", "Isaiah", "Jeremiah",
            "Ezekiel", "Daniel", "Matthew", "Mark", "Luke", "John",
            "Acts", "Romans", "1 Corinthians", "2 Corinthians"
        ]
        
        # Filter based on known chapter counts (simplified)
        suitable_books = []
        
        for book in books_with_many_chapters:
            if self._book_has_chapter(book, chapter):
                suitable_books.append(book)
        
        return suitable_books
    
    def _book_has_chapter(self, book: str, chapter: int) -> bool:
        """Check if a book has the specified chapter (simplified logic)"""
        # Simplified chapter count mapping
        chapter_counts = {
            "Genesis": 50, "Exodus": 40, "Psalms": 150, "Proverbs": 31,
            "Isaiah": 66, "Jeremiah": 52, "Matthew": 28, "Luke": 24,
            "John": 21, "Acts": 28, "Romans": 16, "1 Corinthians": 16
        }
        
        return chapter <= chapter_counts.get(book, 25)  # Default to 25 chapters
    
    def _get_nearby_verse(self, book: str, chapter: int, verse: int) -> Optional[Dict[str, Any]]:
        """Get a nearby verse if exact match not found"""
        # Try verses around the target
        for offset in [0, -1, 1, -2, 2]:
            try_verse = verse + offset
            if try_verse > 0:
                verse_data = self.get_verse(book, chapter, try_verse)
                if verse_data:
                    return verse_data
        
        return None
    
    def _get_fallback_verse_for_time(self, hour: int, minute: int) -> Optional[Dict[str, Any]]:
        """Get a fallback verse for specific time"""
        # Use a simple hash to select from available fallback verses
        verse_keys = list(self.fallback_verses.keys())
        if verse_keys:
            index = (hour * 60 + minute) % len(verse_keys)
            selected_key = verse_keys[index]
            return self.fallback_verses[selected_key].copy()
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache),
            'cache_timeout': self.cache_timeout,
            'fallback_verses': len(self.fallback_verses)
        }

