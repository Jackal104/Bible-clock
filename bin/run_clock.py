#!/usr/bin/env python3
"""
Enhanced Bible Clock Main Application

This is the main entry point for the Bible Clock application with
enhanced features, error handling, and monitoring capabilities.
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
from bible_api import BibleAPI
from verse_manager import VerseManager, VerseScheduler
from display import display_manager
from service_manager import ServiceManager

class BibleClockApp:
    """Enhanced Bible Clock Application"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bible_api = None
        self.verse_manager = None
        self.verse_scheduler = None
        self.service_manager = None
        
        # Application state
        self.initialized = False
        self.last_verse_data = None
        
    def initialize(self) -> bool:
        """Initialize all application components"""
        try:
            self.logger.info("Initializing Bible Clock application")
            
            # Validate configuration
            validation = config.validate_config()
            if not validation['valid']:
                for error in validation['errors']:
                    self.logger.error(f"Configuration error: {error}")
                return False
            
            for warning in validation['warnings']:
                self.logger.warning(f"Configuration warning: {warning}")
            
            # Initialize Bible API
            self.bible_api = BibleAPI(
                api_url=config.BIBLE_API_URL,
                version=config.BIBLE_VERSION,
                fallback_enabled=config.FALLBACK_ENABLED
            )
            self.logger.info("Bible API initialized")
            
            # Initialize verse manager
            self.verse_manager = VerseManager(self.bible_api)
            self.verse_scheduler = VerseScheduler(self.verse_manager)
            self.logger.info("Verse manager initialized")
            
            # Initialize service manager
            self.service_manager = ServiceManager(
                update_callback=self.update_display,
                update_interval=config.UPDATE_INTERVAL,
                startup_delay=config.STARTUP_DELAY
            )
            self.logger.info("Service manager initialized")
            
            self.initialized = True
            self.logger.info("Bible Clock application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            return False
    
    def update_display(self) -> bool:
        """Update the display with current verse"""
        try:
            # Get current verse
            verse_data = self.verse_scheduler.get_current_verse()
            
            if not verse_data:
                self.logger.warning("No verse data available")
                display_manager.display_error("No verse available")
                return False
            
            # Display verse
            success = display_manager.display_verse(verse_data)
            
            if success:
                self.last_verse_data = verse_data
                self.logger.info(f"Successfully displayed: {verse_data.get('reference', 'Unknown')}")
            else:
                self.logger.error("Failed to display verse")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Display update failed: {e}")
            display_manager.display_error(f"Update failed: {str(e)[:50]}")
            return False
    
    def run_once(self) -> bool:
        """Run a single update cycle"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.logger.info("Running single update cycle")
        return self.update_display()
    
    def run_service(self) -> bool:
        """Run as a continuous service"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.logger.info("Starting Bible Clock service")
        
        try:
            # Start service manager
            if self.service_manager.start():
                # Keep main thread alive
                while self.service_manager.running:
                    try:
                        # Service manager handles the scheduling
                        # Main thread just needs to stay alive
                        import time
                        time.sleep(1)
                    except KeyboardInterrupt:
                        self.logger.info("Keyboard interrupt received")
                        break
                
                return True
            else:
                self.logger.error("Failed to start service manager")
                return False
                
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            return False
        finally:
            self.shutdown()
    
    def test_components(self) -> Dict[str, Any]:
        """Test all application components"""
        test_results = {
            'initialization': False,
            'bible_api': False,
            'verse_manager': False,
            'display_manager': False,
            'overall_success': False,
            'errors': []
        }
        
        try:
            # Test initialization
            if self.initialize():
                test_results['initialization'] = True
            else:
                test_results['errors'].append("Initialization failed")
            
            # Test Bible API
            if self.bible_api:
                try:
                    test_verse = self.bible_api.get_verse("John", 3, 16)
                    if test_verse and test_verse.get('text'):
                        test_results['bible_api'] = True
                    else:
                        test_results['errors'].append("Bible API returned no data")
                except Exception as e:
                    test_results['errors'].append(f"Bible API error: {e}")
            
            # Test verse manager
            if self.verse_manager:
                try:
                    test_verse_data = self.verse_manager.get_verse_for_time(12, 0)
                    if test_verse_data:
                        test_results['verse_manager'] = True
                    else:
                        test_results['errors'].append("Verse manager returned no data")
                except Exception as e:
                    test_results['errors'].append(f"Verse manager error: {e}")
            
            # Test display manager
            try:
                display_test = display_manager.test_display()
                test_results['display_manager'] = display_test['overall_success']
                if not display_test['overall_success']:
                    test_results['errors'].extend(display_test['errors'])
            except Exception as e:
                test_results['errors'].append(f"Display manager error: {e}")
            
            # Overall success
            test_results['overall_success'] = (
                test_results['initialization'] and
                test_results['bible_api'] and
                test_results['verse_manager'] and
                test_results['display_manager']
            )
            
        except Exception as e:
            test_results['errors'].append(f"Test error: {e}")
        
        return test_results
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status"""
        status = {
            'initialized': self.initialized,
            'timestamp': datetime.now().isoformat(),
            'last_verse': self.last_verse_data.get('reference') if self.last_verse_data else None
        }
        
        if self.service_manager:
            status['service'] = self.service_manager.get_status()
        
        if display_manager:
            status['display'] = display_manager.get_display_stats()
        
        if self.verse_manager:
            status['verse_stats'] = self.verse_manager.get_verse_statistics()
        
        return status
    
    def shutdown(self):
        """Shutdown application gracefully"""
        self.logger.info("Shutting down Bible Clock application")
        
        try:
            if self.service_manager:
                self.service_manager.stop()
            
            if display_manager:
                display_manager.shutdown()
            
            self.logger.info("Bible Clock application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced Bible Clock Application')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--test', action='store_true', help='Run component tests')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')
    
    args = parser.parse_args()
    
    # Override configuration based on arguments
    if args.debug:
        config.DEBUG_MODE = True
        config.LOG_LEVEL = 'DEBUG'
        config.setup_logging()
    
    if args.simulate:
        config.SIMULATION_MODE = True
    
    # Create application
    app = BibleClockApp()
    
    try:
        if args.test:
            # Run tests
            print("Running component tests...")
            test_results = app.test_components()
            
            print(f"Initialization: {'✓' if test_results['initialization'] else '✗'}")
            print(f"Bible API: {'✓' if test_results['bible_api'] else '✗'}")
            print(f"Verse Manager: {'✓' if test_results['verse_manager'] else '✗'}")
            print(f"Display Manager: {'✓' if test_results['display_manager'] else '✗'}")
            print(f"Overall: {'✓' if test_results['overall_success'] else '✗'}")
            
            if test_results['errors']:
                print("\nErrors:")
                for error in test_results['errors']:
                    print(f"  - {error}")
            
            sys.exit(0 if test_results['overall_success'] else 1)
        
        elif args.status:
            # Show status
            if app.initialize():
                status = app.get_status()
                print("Bible Clock Status:")
                print(f"  Initialized: {status['initialized']}")
                print(f"  Timestamp: {status['timestamp']}")
                print(f"  Last Verse: {status.get('last_verse', 'None')}")
                
                if 'service' in status:
                    service_status = status['service']
                    print(f"  Service Running: {service_status['running']}")
                    print(f"  Updates: {service_status['update_count']}")
                    print(f"  Errors: {service_status['error_count']}")
            else:
                print("Failed to initialize application")
                sys.exit(1)
        
        elif args.once:
            # Run once
            success = app.run_once()
            sys.exit(0 if success else 1)
        
        else:
            # Run as service
            success = app.run_service()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        app.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

