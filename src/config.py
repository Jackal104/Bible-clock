"""
Enhanced Configuration Management for Bible Clock

This module provides comprehensive configuration management with environment
variable support, validation, and default values.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management class with environment variable support"""
    
    def __init__(self):
        self.load_config()
        self.setup_logging()
    
    def load_config(self):
        """Load configuration from environment variables with defaults"""
        
        # Display Configuration
        self.DISPLAY_WIDTH = int(os.getenv('DISPLAY_WIDTH', '1872'))
        self.DISPLAY_HEIGHT = int(os.getenv('DISPLAY_HEIGHT', '1404'))
        self.DISPLAY_TYPE = os.getenv('DISPLAY_TYPE', 'IT8951')
        self.VCOM_VALUE = os.getenv('VCOM_VALUE', '-1.50')
        
        # Bible API Configuration
        self.BIBLE_API_URL = os.getenv('BIBLE_API_URL', 'https://bible-api.com')
        self.BIBLE_VERSION = os.getenv('BIBLE_VERSION', 'kjv')
        self.FALLBACK_ENABLED = os.getenv('FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Timing Configuration
        self.UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '60'))
        self.STARTUP_DELAY = int(os.getenv('STARTUP_DELAY', '30'))
        self.RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', '3'))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', '/var/log/bible-clock.log')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Service Configuration
        self.SERVICE_USER = os.getenv('SERVICE_USER', 'bibleclock')
        self.WORKING_DIRECTORY = os.getenv('WORKING_DIRECTORY', '/home/pi/bible-clock')
        
        # Hardware Configuration
        self.DRIVER_PATH = os.getenv('DRIVER_PATH', '/home/pi/bible-clock-drivers/epd')
        self.VCOM_CONFIG_FILE = os.getenv('VCOM_CONFIG_FILE', '/home/pi/bible-clock-drivers/vcom.conf')
        
        # Performance Configuration
        self.MEMORY_LIMIT_MB = int(os.getenv('MEMORY_LIMIT_MB', '100'))
        self.REFRESH_OPTIMIZATION = os.getenv('REFRESH_OPTIMIZATION', 'true').lower() == 'true'
        self.FULL_REFRESH_INTERVAL = int(os.getenv('FULL_REFRESH_INTERVAL', '10'))
        
        # Font Configuration
        self.FONT_PATH = os.getenv('FONT_PATH', 'data/fonts')
        self.DEFAULT_FONT_SIZE = int(os.getenv('DEFAULT_FONT_SIZE', '48'))
        self.TITLE_FONT_SIZE = int(os.getenv('TITLE_FONT_SIZE', '36'))
        
        # Simulation Mode (for testing without hardware)
        self.SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'false').lower() == 'true'
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler() if self.DEBUG_MODE else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate display configuration
        if self.DISPLAY_WIDTH <= 0 or self.DISPLAY_HEIGHT <= 0:
            validation_results['errors'].append("Invalid display dimensions")
            validation_results['valid'] = False
            
        # Validate VCOM value format
        try:
            vcom_float = float(self.VCOM_VALUE)
            if vcom_float > 0 or vcom_float < -5:
                validation_results['warnings'].append(f"Unusual VCOM value: {self.VCOM_VALUE}")
        except ValueError:
            validation_results['errors'].append(f"Invalid VCOM value format: {self.VCOM_VALUE}")
            validation_results['valid'] = False
            
        # Validate timing configuration
        if self.UPDATE_INTERVAL < 10:
            validation_results['warnings'].append("Very short update interval may cause display issues")
            
        # Validate paths
        if not self.SIMULATION_MODE:
            if not Path(self.DRIVER_PATH).exists():
                validation_results['errors'].append(f"Driver not found: {self.DRIVER_PATH}")
                validation_results['valid'] = False
                
        # Validate font path
        font_path = Path(self.FONT_PATH)
        if not font_path.exists():
            validation_results['warnings'].append(f"Font directory not found: {self.FONT_PATH}")
            
        return validation_results
    
    def get_vcom_from_file(self) -> Optional[str]:
        """Load VCOM value from configuration file if it exists"""
        try:
            if Path(self.VCOM_CONFIG_FILE).exists():
                with open(self.VCOM_CONFIG_FILE, 'r') as f:
                    content = f.read().strip()
                    if content.startswith("VCOM_VALUE="):
                        return content.split("=")[1]
            return None
        except Exception as e:
            self.logger.warning(f"Could not read VCOM config file: {e}")
            return None
    
    def update_vcom_value(self):
        """Update VCOM value from file if available"""
        file_vcom = self.get_vcom_from_file()
        if file_vcom:
            self.VCOM_VALUE = file_vcom
            self.logger.info(f"Updated VCOM value from file: {self.VCOM_VALUE}")

# Global configuration instance
config = Config()

# Legacy compatibility
DEBUG = config.DEBUG_MODE
SIMULATION = config.SIMULATION_MODE

