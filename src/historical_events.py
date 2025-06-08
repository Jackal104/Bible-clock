"""
Historical events module for day-based verse selection.
Maps calendar dates to biblical events and related verses.
"""

import json
import random
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict
import config


class HistoricalEvents:
    """Manages biblical events mapped to calendar dates."""
    
    def __init__(self):
        """Initialize the historical events system."""
        self.events = self._load_historical_events()
        
    def _load_historical_events(self) -> Dict:
        """Load historical biblical events data."""
        # For now, create a basic mapping of biblical events to dates
        # This would ideally be loaded from a JSON file
        events = {
            # January
            1: {
                1: ["Genesis 1:1", "Colossians 1:16", "Hebrews 1:2"],  # New Year - Creation theme
                6: ["Matthew 2:1-12", "Isaiah 60:3"],  # Epiphany
                15: ["1 Samuel 16:13", "Psalms 23:1"],  # Example historical date
            },
            # February  
            2: {
                14: ["1 Corinthians 13:4-8", "Song of Solomon 2:10-13"],  # Valentine's Day - Love theme
                29: ["Psalms 90:12", "Ecclesiastes 3:1"],  # Leap year - Time theme
            },
            # March
            3: {
                17: ["Romans 10:12", "Galatians 3:28"],  # St. Patrick's Day - Unity theme
                21: ["Ecclesiastes 3:1", "Genesis 1:14"],  # Spring Equinox
            },
            # April (Nisan - Passover month)
            4: {
                1: ["Psalms 126:2", "Proverbs 17:22"],  # April Fool's - Joy/Laughter
                14: ["Exodus 12:1-14", "1 Corinthians 5:7"],  # Passover (approximate)
                15: ["Matthew 28:1-10", "1 Corinthians 15:20"],  # Easter (approximate)
                22: ["Genesis 1:11-13", "Psalms 104:14"],  # Earth Day
            },
            # May
            5: {
                1: ["Psalms 104:10-16", "Genesis 8:22"],  # May Day - Spring/Growth
                10: ["Proverbs 31:28", "Exodus 20:12"],  # Mother's Day (approximate)
                25: ["Acts 2:1-4", "Joel 2:28"],  # Pentecost (approximate)
            },
            # June (Sivan - Pentecost month)
            6: {
                15: ["Proverbs 20:29", "Psalms 71:18"],  # Father's Day (approximate)
                21: ["Psalms 74:16", "Genesis 1:14"],  # Summer Solstice
            },
            # July
            7: {
                4: ["Galatians 5:1", "2 Corinthians 3:17"],  # Independence Day
                15: ["Psalms 126:3", "Nehemiah 8:10"],  # Mid-summer celebration
            },
            # August
            8: {
                15: ["Psalms 67:6", "Deuteronomy 8:7-10"],  # Harvest theme
            },
            # September (Tishrei - High Holy Days)
            9: {
                1: ["Leviticus 23:24", "Numbers 29:1"],  # Rosh Hashanah (approximate)
                10: ["Leviticus 16:30", "Hebrews 9:7"],  # Yom Kippur (approximate)
                15: ["Leviticus 23:34", "Nehemiah 8:14-17"],  # Sukkot (approximate)
                22: ["Ecclesiastes 3:1", "Genesis 1:14"],  # Autumn Equinox
            },
            # October
            10: {
                31: ["1 John 4:18", "Psalms 27:1"],  # Halloween - Light over darkness
            },
            # November
            11: {
                11: ["John 15:13", "Romans 13:7"],  # Veterans Day
                25: ["Psalms 100:4", "1 Thessalonians 5:18"],  # Thanksgiving (approximate)
            },
            # December (Kislev/Tevet - Hanukkah/Christmas)
            12: {
                8: ["1 Maccabees 4:52-59", "John 8:12"],  # Hanukkah (approximate)
                21: ["John 1:5", "Isaiah 9:2"],  # Winter Solstice - Light theme
                25: ["Luke 2:1-20", "Matthew 1:21", "Isaiah 9:6"],  # Christmas
                31: ["Psalms 90:12", "2 Corinthians 5:17"],  # New Year's Eve
            }
        }
        
        return events
    
    def get_verses_for_date(self, target_date: date = None) -> List[str]:
        """
        Get verses for a specific date.
        
        Args:
            target_date: Date to get verses for. Uses today if None.
            
        Returns:
            List of verse references for the date
        """
        if target_date is None:
            target_date = date.today()
        
        month = target_date.month
        day = target_date.day
        
        # Check for exact date match
        if month in self.events and day in self.events[month]:
            return self.events[month][day]
        
        # Fallback to month-level events
        month_events = []
        if month in self.events:
            for day_events in self.events[month].values():
                month_events.extend(day_events)
        
        if month_events:
            return month_events
        
        # Fallback to seasonal events
        season_events = self._get_seasonal_verses(month)
        if season_events:
            return season_events
        
        # Ultimate fallback
        return ["John 3:16", "Psalms 23:1", "Romans 8:28"]
    
    def _get_seasonal_verses(self, month: int) -> List[str]:
        """Get verses based on the season."""
        seasonal_verses = {
            'spring': [
                "Song of Solomon 2:11-12", "Isaiah 43:19", "2 Corinthians 5:17",
                "Ecclesiastes 3:1", "Genesis 8:22"
            ],
            'summer': [
                "Psalms 74:17", "Jeremiah 8:20", "Proverbs 6:8",
                "Psalms 104:19", "Genesis 1:14"
            ],
            'autumn': [
                "Ecclesiastes 3:1", "Psalms 1:3", "Galatians 6:9",
                "2 Timothy 4:2", "Psalms 126:5-6"
            ],
            'winter': [
                "Isaiah 55:10-11", "Psalms 147:16-18", "Job 37:6",
                "Isaiah 1:18", "Psalms 51:7"
            ]
        }
        
        for season, months in config.SEASONS.items():
            if month in months:
                return seasonal_verses.get(season, [])
        
        return []
    
    def get_random_verse_for_date(self, target_date: date = None) -> Tuple[str, str]:
        """
        Get a random verse for a specific date.
        
        Args:
            target_date: Date to get verse for. Uses today if None.
            
        Returns:
            Tuple of (verse_reference, description)
        """
        verses = self.get_verses_for_date(target_date)
        
        if not verses:
            return ("John 3:16", "Default verse")
        
        selected_verse = random.choice(verses)
        
        # Generate description based on date
        if target_date is None:
            target_date = date.today()
        
        description = self._get_date_description(target_date)
        
        return (selected_verse, description)
    
    def _get_date_description(self, target_date: date) -> str:
        """Generate a description for the date."""
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        month = target_date.month
        day = target_date.day
        
        # Check for special dates
        special_dates = {
            (1, 1): "New Year's Day",
            (2, 14): "Valentine's Day", 
            (3, 17): "St. Patrick's Day",
            (4, 1): "April Fool's Day",
            (7, 4): "Independence Day",
            (10, 31): "Halloween",
            (12, 25): "Christmas Day",
            (12, 31): "New Year's Eve"
        }
        
        if (month, day) in special_dates:
            return special_dates[(month, day)]
        
        # Check for biblical calendar events
        biblical_events = {
            3: "Nisan (Passover Month)",
            4: "Iyyar", 
            5: "Sivan (Pentecost Month)",
            9: "Tishrei (High Holy Days)",
            12: "Kislev/Tevet (Hanukkah Season)"
        }
        
        if month in biblical_events:
            return f"{month_names[month-1]} - {biblical_events[month]}"
        
        # Default description
        return f"{month_names[month-1]} {day}"
    
    def get_statistics(self) -> Dict:
        """Get statistics about historical events coverage."""
        total_days = 0
        covered_days = 0
        
        for month in range(1, 13):
            days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1]
            total_days += days_in_month
            
            if month in self.events:
                covered_days += len(self.events[month])
        
        return {
            'total_days': total_days,
            'covered_days': covered_days,
            'coverage_percentage': round((covered_days / total_days) * 100, 1),
            'months_with_events': len(self.events),
            'total_events': sum(len(month_events) for month_events in self.events.values())
        }

