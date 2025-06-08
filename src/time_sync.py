"""
Network time synchronization module for Bible Clock.
Ensures accurate time and date for proper verse selection.
"""

import os
import subprocess
import time
import socket
from datetime import datetime, timezone
from typing import Optional, Tuple
import config

class TimeSync:
    """Handles network time synchronization and timezone management."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize time synchronization.
        
        Args:
            debug: Enable debug output
        """
        self.debug = debug
        self.last_sync_attempt = 0
        self.sync_successful = False
        
    def check_internet_connection(self) -> bool:
        """
        Check if internet connection is available.
        
        Returns:
            True if internet is available, False otherwise
        """
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            if self.debug:
                print("Internet connection available")
            return True
        except OSError:
            if self.debug:
                print("No internet connection")
            return False
    
    def sync_time_with_ntp(self) -> bool:
        """
        Synchronize system time with NTP servers.
        
        Returns:
            True if sync successful, False otherwise
        """
        if not self.check_internet_connection():
            return False
            
        current_time = time.time()
        if current_time - self.last_sync_attempt < config.TIME_SYNC_RETRY_INTERVAL:
            return self.sync_successful
            
        self.last_sync_attempt = current_time
        
        # Try each NTP server
        for ntp_server in config.NTP_SERVERS:
            try:
                if self.debug:
                    print(f"Attempting time sync with {ntp_server}")
                
                # Use ntpdate if available, otherwise use timedatectl
                result = self._sync_with_server(ntp_server)
                if result:
                    self.sync_successful = True
                    if self.debug:
                        print(f"Time synchronized successfully with {ntp_server}")
                        print(f"Current time: {datetime.now()}")
                    return True
                    
            except Exception as e:
                if self.debug:
                    print(f"Failed to sync with {ntp_server}: {e}")
                continue
        
        self.sync_successful = False
        if self.debug:
            print("Failed to sync time with any NTP server")
        return False
    
    def _sync_with_server(self, ntp_server: str) -> bool:
        """
        Sync time with a specific NTP server.
        
        Args:
            ntp_server: NTP server hostname
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try timedatectl first (systemd)
            result = subprocess.run(
                ['sudo', 'timedatectl', 'set-ntp', 'true'],
                capture_output=True, text=True, timeout=config.TIME_SYNC_TIMEOUT
            )
            
            if result.returncode == 0:
                # Force immediate sync
                subprocess.run(
                    ['sudo', 'systemctl', 'restart', 'systemd-timesyncd'],
                    capture_output=True, text=True, timeout=10
                )
                time.sleep(2)  # Wait for sync
                return True
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # Try ntpdate as fallback
            result = subprocess.run(
                ['sudo', 'ntpdate', '-s', ntp_server],
                capture_output=True, text=True, timeout=config.TIME_SYNC_TIMEOUT
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def set_timezone(self, timezone_name: str = None) -> bool:
        """
        Set system timezone.
        
        Args:
            timezone_name: Timezone name (e.g., 'America/New_York')
            
        Returns:
            True if successful, False otherwise
        """
        if timezone_name is None:
            timezone_name = config.TIMEZONE
            
        try:
            if self.debug:
                print(f"Setting timezone to {timezone_name}")
            
            # Use timedatectl to set timezone
            result = subprocess.run(
                ['sudo', 'timedatectl', 'set-timezone', timezone_name],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                if self.debug:
                    print(f"Timezone set successfully to {timezone_name}")
                return True
            else:
                if self.debug:
                    print(f"Failed to set timezone: {result.stderr}")
                return False
                
        except Exception as e:
            if self.debug:
                print(f"Error setting timezone: {e}")
            return False
    
    def get_current_datetime(self) -> datetime:
        """
        Get current date and time.
        
        Returns:
            Current datetime object
        """
        return datetime.now()
    
    def get_date_info(self) -> Tuple[int, int, int, str, str]:
        """
        Get comprehensive date information for verse selection.
        
        Returns:
            Tuple of (month, day, year, month_name, season)
        """
        now = self.get_current_datetime()
        month = now.month
        day = now.day
        year = now.year
        month_name = now.strftime("%B")
        
        # Determine season based on month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:  # 9, 10, 11
            season = "Autumn"
        
        return month, day, year, month_name, season
    
    def validate_time_accuracy(self) -> bool:
        """
        Validate that system time appears accurate.
        
        Returns:
            True if time seems reasonable, False otherwise
        """
        now = datetime.now()
        
        # Check if year is reasonable (between 2020 and 2050)
        if not (2020 <= now.year <= 2050):
            if self.debug:
                print(f"Year {now.year} seems unreasonable")
            return False
        
        # Check if date components are valid
        if not (1 <= now.month <= 12):
            if self.debug:
                print(f"Month {now.month} is invalid")
            return False
            
        if not (1 <= now.day <= 31):
            if self.debug:
                print(f"Day {now.day} is invalid")
            return False
        
        if self.debug:
            print(f"Time validation passed: {now}")
        return True
    
    def ensure_time_sync(self) -> bool:
        """
        Ensure system time is synchronized.
        This is the main method to call for time synchronization.
        
        Returns:
            True if time is synchronized and accurate, False otherwise
        """
        if self.debug:
            print("Ensuring time synchronization...")
        
        # First check if time seems reasonable
        if self.validate_time_accuracy():
            if self.debug:
                print("System time appears accurate")
            return True
        
        # Set timezone first
        self.set_timezone()
        
        # Attempt NTP sync
        if self.sync_time_with_ntp():
            # Wait a moment and validate again
            time.sleep(2)
            return self.validate_time_accuracy()
        
        if self.debug:
            print("Time synchronization failed")
        return False
    
    def get_status(self) -> dict:
        """
        Get time synchronization status.
        
        Returns:
            Dictionary with sync status information
        """
        now = self.get_current_datetime()
        month, day, year, month_name, season = self.get_date_info()
        
        return {
            'current_time': now.strftime("%Y-%m-%d %H:%M:%S"),
            'timezone': config.TIMEZONE,
            'date_info': {
                'month': month,
                'day': day,
                'year': year,
                'month_name': month_name,
                'season': season
            },
            'sync_successful': self.sync_successful,
            'last_sync_attempt': self.last_sync_attempt,
            'internet_available': self.check_internet_connection(),
            'ntp_servers': config.NTP_SERVERS
        }

