"""
Time utilities for the Bible Clock.
Handles 12-hour time parsing and CLI overrides.
"""

from datetime import datetime
from typing import Tuple
import argparse


def parse_12_hour_time(time_str: str) -> Tuple[int, int]:
    """
    Parse a 12-hour format time string and return hour and minute.
    
    Args:
        time_str: Time string in format "H:MM AM/PM" (e.g., "2:37 PM")
        
    Returns:
        Tuple of (hour, minute) where hour is 1-12
        
    Raises:
        ValueError: If time string is invalid
    """
    try:
        # Parse the time string
        dt = datetime.strptime(time_str.strip(), "%I:%M %p")
        hour = dt.hour
        minute = dt.minute
        
        # Convert 24-hour to 12-hour format
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour = hour - 12
            
        return hour, minute
    except ValueError as e:
        raise ValueError(f"Invalid time format '{time_str}'. Expected format: 'H:MM AM/PM'") from e


def get_current_time() -> Tuple[int, int]:
    """
    Get the current time in 12-hour format.
    
    Returns:
        Tuple of (hour, minute) where hour is 1-12
    """
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    # Convert 24-hour to 12-hour format
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour = hour - 12
        
    return hour, minute


def get_time_from_args_or_current(args: argparse.Namespace = None) -> Tuple[int, int]:
    """
    Get time from command line arguments or current time.
    
    Args:
        args: Parsed command line arguments with optional 'time' attribute
        
    Returns:
        Tuple of (hour, minute) where hour is 1-12
    """
    if args and hasattr(args, 'time') and args.time:
        return parse_12_hour_time(args.time)
    else:
        return get_current_time()


def format_time_12_hour(hour: int, minute: int) -> str:
    """
    Format hour and minute into 12-hour time string.
    
    Args:
        hour: Hour (1-12)
        minute: Minute (0-59)
        
    Returns:
        Formatted time string like "2:37 PM"
    """
    # Determine AM/PM
    if hour == 12:
        period = "PM"
        display_hour = 12
    elif hour > 12:
        period = "PM"
        display_hour = hour - 12
    else:
        period = "AM"
        display_hour = hour
        if hour == 0:
            display_hour = 12
    
    return f"{display_hour}:{minute:02d} {period}"

