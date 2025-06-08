"""
ChatGPT API integration for Bible verse explanations.
Provides contextual information about Bible verses.
"""

import json
import time
from typing import Optional, Dict, Any
import config

# OpenAI API dependency
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class ChatGPTExplainer:
    """Provides Bible verse explanations using ChatGPT API."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize ChatGPT explainer.
        
        Args:
            debug: Enable debug output
        """
        self.debug = debug
        self.enabled = bool(config.CHATGPT_API_KEY and config.CHATGPT_API_KEY != 'your_openai_api_key_here')
        self.api_key = config.CHATGPT_API_KEY
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds between requests
        
        # Cache for explanations
        self.explanation_cache = {}
        self.max_cache_size = 100
        
        if self.enabled and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
            if self.debug:
                print("ChatGPT API initialized")
        elif self.debug:
            if not self.enabled:
                print("ChatGPT API disabled - no API key configured")
            if not OPENAI_AVAILABLE:
                print("OpenAI library not available")
    
    def explain_verse(self, book: str, chapter: int, verse: int, verse_text: str) -> Optional[str]:
        """
        Get explanation for a Bible verse.
        
        Args:
            book: Book name
            chapter: Chapter number
            verse: Verse number
            verse_text: The verse text
            
        Returns:
            Explanation text or None if failed
        """
        if not self.enabled:
            if self.debug:
                print("ChatGPT API not enabled")
            return None
        
        # Create cache key
        cache_key = f"{book}_{chapter}_{verse}"
        
        # Check cache first
        if cache_key in self.explanation_cache:
            if self.debug:
                print(f"Using cached explanation for {book} {chapter}:{verse}")
            return self.explanation_cache[cache_key]
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        
        try:
            # Prepare the prompt
            verse_ref = f"{book} {chapter}:{verse}"
            prompt = self._create_explanation_prompt(verse_ref, verse_text)
            
            if self.debug:
                print(f"Requesting explanation for {verse_ref}")
            
            # Make API request
            explanation = self._make_api_request(prompt)
            
            if explanation:
                # Cache the result
                self._cache_explanation(cache_key, explanation)
                
                if self.debug:
                    print(f"Received explanation for {verse_ref}")
                
                return explanation
            
        except Exception as e:
            if self.debug:
                print(f"Error getting verse explanation: {e}")
        
        finally:
            self.last_request_time = time.time()
        
        return None
    
    def _create_explanation_prompt(self, verse_ref: str, verse_text: str) -> str:
        """
        Create a prompt for verse explanation.
        
        Args:
            verse_ref: Verse reference (e.g., "John 3:16")
            verse_text: The verse text
            
        Returns:
            Formatted prompt for ChatGPT
        """
        prompt = f"""Please provide a brief, clear explanation of this Bible verse in 2-3 sentences suitable for audio reading:

Verse: {verse_ref}
Text: "{verse_text}"

Focus on:
- The main meaning or message
- Historical or cultural context if relevant
- How it applies to daily life

Keep the explanation conversational and easy to understand when spoken aloud. Limit to about 50 words."""
        
        return prompt
    
    def _make_api_request(self, prompt: str) -> Optional[str]:
        """
        Make API request to ChatGPT.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Response text or None if failed
        """
        try:
            if OPENAI_AVAILABLE:
                # Use OpenAI library
                response = openai.ChatCompletion.create(
                    model=config.CHATGPT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful Bible study assistant who provides clear, concise explanations of Bible verses."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=config.CHATGPT_MAX_TOKENS,
                    temperature=0.7
                )
                
                return response.choices[0].message.content.strip()
                
            elif REQUESTS_AVAILABLE:
                # Use direct API call
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': config.CHATGPT_MODEL,
                    'messages': [
                        {"role": "system", "content": "You are a helpful Bible study assistant who provides clear, concise explanations of Bible verses."},
                        {"role": "user", "content": prompt}
                    ],
                    'max_tokens': config.CHATGPT_MAX_TOKENS,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    if self.debug:
                        print(f"API request failed: {response.status_code}")
                    return None
            
        except Exception as e:
            if self.debug:
                print(f"API request error: {e}")
            return None
    
    def _cache_explanation(self, cache_key: str, explanation: str):
        """
        Cache an explanation.
        
        Args:
            cache_key: Key for caching
            explanation: Explanation to cache
        """
        # Manage cache size
        if len(self.explanation_cache) >= self.max_cache_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.explanation_cache))
            del self.explanation_cache[oldest_key]
        
        self.explanation_cache[cache_key] = explanation
    
    def get_contextual_info(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """
        Get contextual information about a verse location.
        
        Args:
            book: Book name
            chapter: Chapter number
            verse: Verse number
            
        Returns:
            Contextual information or None
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Provide brief context about {book} {chapter}:{verse} in 1-2 sentences:
- What book/section of the Bible is this from?
- Who wrote it and when (approximately)?
- What's the main theme of this chapter?

Keep it concise and suitable for audio reading."""
            
            return self._make_api_request(prompt)
            
        except Exception as e:
            if self.debug:
                print(f"Error getting contextual info: {e}")
            return None
    
    def explain_historical_event(self, event_description: str, date: str) -> Optional[str]:
        """
        Get explanation for historical biblical events.
        
        Args:
            event_description: Description of the event
            date: Date context (e.g., "June 8")
            
        Returns:
            Explanation or None
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Briefly explain this biblical event in 2-3 sentences suitable for audio:

Event: {event_description}
Date context: {date}

Focus on:
- What happened and why it's significant
- Key people involved
- Spiritual or historical importance

Keep it conversational and under 60 words."""
            
            return self._make_api_request(prompt)
            
        except Exception as e:
            if self.debug:
                print(f"Error explaining historical event: {e}")
            return None
    
    def clear_cache(self):
        """Clear the explanation cache."""
        self.explanation_cache.clear()
        if self.debug:
            print("Explanation cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            'cache_size': len(self.explanation_cache),
            'max_cache_size': self.max_cache_size,
            'cached_verses': list(self.explanation_cache.keys())
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get ChatGPT explainer status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'enabled': self.enabled,
            'api_key_configured': bool(self.api_key and self.api_key != 'your_openai_api_key_here'),
            'openai_available': OPENAI_AVAILABLE,
            'requests_available': REQUESTS_AVAILABLE,
            'model': config.CHATGPT_MODEL,
            'max_tokens': config.CHATGPT_MAX_TOKENS,
            'rate_limit_interval': self.min_request_interval,
            'cache_stats': self.get_cache_stats()
        }


class MockChatGPTExplainer:
    """Mock ChatGPT explainer for testing and simulation."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.enabled = True
        
        # Sample explanations for testing
        self.sample_explanations = {
            "john_3_16": "This famous verse summarizes God's love for humanity. It explains that God gave His son Jesus as a sacrifice so that anyone who believes in Him can have eternal life. It's often called the 'Gospel in a nutshell' because it captures the core Christian message of salvation through faith.",
            
            "psalms_23_1": "This verse begins the beloved Shepherd's Psalm. David compares God to a shepherd who provides for and protects his sheep. It expresses complete trust and confidence that God will meet all our needs, both physical and spiritual.",
            
            "romans_8_28": "Paul reminds believers that God works everything together for good for those who love Him. This doesn't mean everything that happens is good, but that God can use even difficult circumstances to accomplish His purposes in our lives.",
            
            "default": "This verse contains timeless wisdom and spiritual truth. It was written to encourage and guide believers in their faith journey. The message remains relevant for Christians today as they seek to live according to God's will."
        }
    
    def explain_verse(self, book: str, chapter: int, verse: int, verse_text: str) -> Optional[str]:
        """Mock verse explanation."""
        # Create a key for lookup
        key = f"{book.lower().replace(' ', '_')}_{chapter}_{verse}"
        
        # Return sample explanation or default
        explanation = self.sample_explanations.get(key, self.sample_explanations["default"])
        
        if self.debug:
            print(f"Mock explanation for {book} {chapter}:{verse}")
        
        return explanation
    
    def get_contextual_info(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """Mock contextual information."""
        return f"{book} was written to provide spiritual guidance and encouragement. This chapter focuses on key themes of faith, hope, and God's relationship with His people."
    
    def explain_historical_event(self, event_description: str, date: str) -> Optional[str]:
        """Mock historical event explanation."""
        return f"This biblical event on {date} demonstrates God's faithfulness and power throughout history. It serves as an important reminder of His ongoing work in the world."
    
    def clear_cache(self):
        """Mock cache clear."""
        pass
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Mock cache stats."""
        return {
            'cache_size': 3,
            'max_cache_size': 100,
            'cached_verses': ['john_3_16', 'psalms_23_1', 'romans_8_28']
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Mock status."""
        return {
            'enabled': True,
            'api_key_configured': False,
            'openai_available': False,
            'requests_available': True,
            'model': 'mock-gpt-3.5-turbo',
            'max_tokens': 150,
            'rate_limit_interval': 2,
            'cache_stats': self.get_cache_stats(),
            'mock_mode': True
        }

