"""
Unit tests for time utilities.
"""

import unittest
import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from time_utils import (
    parse_12_hour_time, 
    get_current_time, 
    format_time_12_hour,
    get_time_from_args_or_current
)


class TestTimeUtils(unittest.TestCase):
    """Test cases for time utility functions."""
    
    def test_parse_12_hour_time_valid(self):
        """Test parsing valid 12-hour time strings."""
        test_cases = [
            ("12:00 AM", (12, 0)),
            ("12:00 PM", (12, 0)),
            ("1:00 AM", (1, 0)),
            ("1:00 PM", (1, 0)),
            ("11:59 PM", (11, 59)),
            ("2:37 PM", (2, 37)),
            ("6:15 AM", (6, 15)),
            ("10:30 PM", (10, 30))
        ]
        
        for time_str, expected in test_cases:
            with self.subTest(time_str=time_str):
                result = parse_12_hour_time(time_str)
                self.assertEqual(result, expected)
    
    def test_parse_12_hour_time_invalid(self):
        """Test parsing invalid 12-hour time strings."""
        invalid_cases = [
            "25:00 PM",  # Invalid hour
            "12:60 AM",  # Invalid minute
            "12:00",     # Missing AM/PM
            "12:00 XM",  # Invalid period
            "abc:def AM", # Non-numeric
            "",          # Empty string
            "12 AM",     # Missing colon
            "12:00AM",   # Missing space
        ]
        
        for time_str in invalid_cases:
            with self.subTest(time_str=time_str):
                with self.assertRaises(ValueError):
                    parse_12_hour_time(time_str)
    
    def test_get_current_time(self):
        """Test getting current time."""
        hour, minute = get_current_time()
        
        # Check that values are in valid ranges
        self.assertIsInstance(hour, int)
        self.assertIsInstance(minute, int)
        self.assertGreaterEqual(hour, 1)
        self.assertLessEqual(hour, 12)
        self.assertGreaterEqual(minute, 0)
        self.assertLessEqual(minute, 59)
    
    def test_format_time_12_hour(self):
        """Test formatting time to 12-hour string."""
        test_cases = [
            ((12, 0), "12:00 PM"),
            ((1, 0), "1:00 AM"),
            ((11, 59), "11:59 AM"),
            ((2, 37), "2:37 AM"),
            ((6, 15), "6:15 AM"),
            ((10, 30), "10:30 AM")
        ]
        
        for (hour, minute), expected in test_cases:
            with self.subTest(hour=hour, minute=minute):
                result = format_time_12_hour(hour, minute)
                self.assertEqual(result, expected)
    
    def test_format_time_12_hour_edge_cases(self):
        """Test formatting edge cases."""
        # Test midnight and noon
        self.assertEqual(format_time_12_hour(12, 0), "12:00 PM")
        
        # Test single digit minutes
        self.assertEqual(format_time_12_hour(1, 5), "1:05 AM")
        self.assertEqual(format_time_12_hour(12, 9), "12:09 PM")
    
    def test_round_trip_conversion(self):
        """Test that parsing and formatting are consistent."""
        test_times = [
            "12:00 AM", "12:00 PM", "1:00 AM", "1:00 PM",
            "11:59 AM", "11:59 PM", "2:37 AM", "2:37 PM",
            "6:15 AM", "6:15 PM", "10:30 AM", "10:30 PM"
        ]
        
        for time_str in test_times:
            with self.subTest(time_str=time_str):
                # Parse the time
                hour, minute = parse_12_hour_time(time_str)
                
                # Format it back
                formatted = format_time_12_hour(hour, minute)
                
                # Should match original (accounting for potential formatting differences)
                reparsed_hour, reparsed_minute = parse_12_hour_time(formatted)
                self.assertEqual((hour, minute), (reparsed_hour, reparsed_minute))
    
    def test_get_time_from_args_or_current_with_args(self):
        """Test getting time from arguments."""
        # Mock args object
        class MockArgs:
            def __init__(self, time_str):
                self.time = time_str
        
        # Test with specific time
        args = MockArgs("2:37 PM")
        hour, minute = get_time_from_args_or_current(args)
        self.assertEqual((hour, minute), (2, 37))
        
        # Test with None time
        args = MockArgs(None)
        hour, minute = get_time_from_args_or_current(args)
        self.assertIsInstance(hour, int)
        self.assertIsInstance(minute, int)
    
    def test_get_time_from_args_or_current_without_args(self):
        """Test getting time without arguments."""
        hour, minute = get_time_from_args_or_current(None)
        
        # Should return current time
        self.assertIsInstance(hour, int)
        self.assertIsInstance(minute, int)
        self.assertGreaterEqual(hour, 1)
        self.assertLessEqual(hour, 12)
        self.assertGreaterEqual(minute, 0)
        self.assertLessEqual(minute, 59)
    
    def test_time_consistency(self):
        """Test that time functions are consistent with each other."""
        # Get current time
        current_hour, current_minute = get_current_time()
        
        # Format it
        formatted = format_time_12_hour(current_hour, current_minute)
        
        # Parse it back
        parsed_hour, parsed_minute = parse_12_hour_time(formatted)
        
        # Should match
        self.assertEqual((current_hour, current_minute), (parsed_hour, parsed_minute))


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)

