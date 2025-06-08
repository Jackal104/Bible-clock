"""
Configuration constants for the Bible Clock application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Display settings
DISPLAY_WIDTH = int(os.getenv('DISPLAY_WIDTH', 1200))
DISPLAY_HEIGHT = int(os.getenv('DISPLAY_HEIGHT', 825))
FONT_SIZE = int(os.getenv('FONT_SIZE', 100))

# GPIO pin assignments (Raspberry Pi only)
BUTTON_1_PIN = 18  # Mode cycling button (clock ↔ day mode)
BUTTON_2_PIN = 19  # Version toggle button (KJV ↔ KJV+Amplified)
BUTTON_3_PIN = 20  # Audio/Voice button (TTS, voice commands, ChatGPT)

# Font settings with cross-platform compatibility and fallback
import platform

def get_font_path():
    # Try the custom font first (works on most systems)
    custom_font = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'RobotoMono-Regular.ttf')
    
    # Test if custom font works
    try:
        from PIL import ImageFont
        ImageFont.truetype(custom_font, 12)  # Test load
        return custom_font
    except:
        # Fallback to system fonts
        if platform.system() == "Windows":
            return "C:/Windows/Fonts/arial.ttf"
        elif platform.system() == "Darwin":  # macOS
            return "/System/Library/Fonts/Arial.ttf"
        else:  # Linux/Raspberry Pi
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DEFAULT_FONT_PATH = get_font_path()

# Simulation mode
SIMULATE = os.getenv('SIMULATE', '0').lower() in ('1', 'true', 'yes', 'on')
DEBUG = os.getenv('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')

# Audio and Voice Control Settings
AUDIO_ENABLED = os.getenv('AUDIO_ENABLED', '1').lower() in ('1', 'true', 'yes', 'on')
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY', 'your_openai_api_key_here')

# Voice control settings
WAKE_WORD = "bible clock"
VOICE_TIMEOUT = 5  # seconds to listen for voice commands
VOICE_RECOGNITION_TIMEOUT = 3  # seconds for speech recognition
AUDIO_FEEDBACK = True  # Enable audio feedback for commands

# TTS (Text-to-Speech) settings
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 0.8  # Volume level (0.0 to 1.0)

# Bible data
BIBLE_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'kjv.json')
AMPLIFIED_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'amplified.json')

# Refresh settings
REFRESH_INTERVAL = 60  # seconds

# WiFi and Network settings
WIFI_SSID = os.getenv('WIFI_SSID', 'YourNetworkName')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD', 'YourNetworkPassword')
NTP_SERVERS = os.getenv('NTP_SERVERS', 'pool.ntp.org,time.google.com,time.cloudflare.com').split(',')
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')

# Time sync settings
TIME_SYNC_TIMEOUT = 30  # seconds to wait for time sync
TIME_SYNC_RETRY_INTERVAL = 300  # 5 minutes between sync attempts

# Display modes
CLOCK_MODE = "clock"
DAY_MODE = "day"
DEFAULT_MODE = CLOCK_MODE

# Bible versions
KJV_ONLY = "kjv_only"
KJV_AMPLIFIED = "kjv_amplified"
DEFAULT_VERSION = KJV_ONLY

# Layout settings
VERSE_TEXT_MARGIN = 80
REFERENCE_MARGIN = 50
SIDE_BY_SIDE_MARGIN = 20

# Historical events and seasons
SEASONS = {
    'spring': [3, 4, 5],    # March, April, May
    'summer': [6, 7, 8],    # June, July, August
    'autumn': [9, 10, 11],  # September, October, November
    'winter': [12, 1, 2]    # December, January, February
}

# Biblical calendar mapping (approximate Gregorian equivalents)
BIBLICAL_MONTHS = {
    'nisan': 3,      # March-April (Passover month)
    'iyyar': 4,      # April-May
    'sivan': 5,      # May-June (Pentecost month)
    'tammuz': 6,     # June-July
    'av': 7,         # July-August
    'elul': 8,       # August-September
    'tishrei': 9,    # September-October (High Holy Days)
    'cheshvan': 10,  # October-November
    'kislev': 11,    # November-December (Hanukkah)
    'tevet': 12,     # December-January
    'shevat': 1,     # January-February
    'adar': 2        # February-March (Purim month)
}

# Chapter expansion settings (for "Expand" voice command)
CHAPTER_EXPANSION_ENABLED = True
CHAPTER_EXPANSION_VERSE_DISPLAY_TIME = 3  # seconds per verse
CHAPTER_EXPANSION_MAX_VERSES = 20  # maximum verses to show in expansion

