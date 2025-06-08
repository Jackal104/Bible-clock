"""
Configuration constants for the Bible Clock application.
"""

import os

# Display settings
DISPLAY_WIDTH = int(os.getenv('DISPLAY_WIDTH', 1200))
DISPLAY_HEIGHT = int(os.getenv('DISPLAY_HEIGHT', 825))
FONT_SIZE = int(os.getenv('FONT_SIZE', 48))  # Increased from 24 to 48

# GPIO pin assignments (Raspberry Pi only)
BUTTON_1_PIN = 18  # Mode cycling button (clock ↔ day mode)
BUTTON_2_PIN = 19  # Version toggle button (KJV ↔ KJV+Amplified)

# Font settings
DEFAULT_FONT_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'RobotoMono-Regular.ttf')

# Simulation mode
SIMULATE = os.getenv('SIMULATE', '0').lower() in ('1', 'true', 'yes', 'on')
DEBUG = os.getenv('DEBUG', '0').lower() in ('1', 'true', 'yes', 'on')

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

