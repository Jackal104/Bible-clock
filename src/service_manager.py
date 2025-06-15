"""
Service Manager

This module handles service lifecycle, monitoring, and management
for the Bible Clock application.
"""

import logging
import signal
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
import psutil
import os

class ServiceManager:
    """Enhanced service manager with monitoring and lifecycle management"""
    
    def __init__(self, update_callback: Callable = None, 
                 update_interval: int = 60, startup_delay: int = 30):
        self.logger = logging.getLogger(__name__)
        self.update_callback = update_callback
        self.update_interval = update_interval
        self.startup_delay = startup_delay
        
        # Service state
        self.running = False
        self.paused = False
        self.shutdown_requested = False
        
        # Monitoring
        self.start_time = None
        self.last_update_time = None
        self.update_count = 0
        self.error_count = 0
        self.last_error = None
        
        # Threading
        self.main_thread = None
        self.monitor_thread = None
        self.update_lock = threading.Lock()
        
        # Performance tracking
        self.performance_stats = {
            'avg_update_time': 0,
            'max_update_time': 0,
            'min_update_time': float('inf'),
            'update_times': []
        }
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            self.shutdown()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def start(self) -> bool:
        """Start the service"""
        try:
            if self.running:
                self.logger.warning("Service already running")
                return True
            
            self.logger.info("Starting Bible Clock service")
            self.start_time = datetime.now()
            self.running = True
            self.shutdown_requested = False
            
            # Startup delay
            if self.startup_delay > 0:
                self.logger.info(f"Startup delay: {self.startup_delay} seconds")
                time.sleep(self.startup_delay)
            
            # Start main service thread
            self.main_thread = threading.Thread(target=self._main_loop, daemon=False)
            self.main_thread.start()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("Bible Clock service started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            self.running = False
            return False
    
    def stop(self):
        """Stop the service"""
        self.logger.info("Stopping Bible Clock service")
        self.running = False
        
        # Wait for threads to finish
        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join(timeout=10)
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Bible Clock service stopped")
    
    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Initiating graceful shutdown")
        self.shutdown_requested = True
        self.stop()
        sys.exit(0)
    
    def pause(self):
        """Pause the service"""
        self.logger.info("Pausing service")
        self.paused = True
    
    def resume(self):
        """Resume the service"""
        self.logger.info("Resuming service")
        self.paused = False
    
    def _main_loop(self):
        """Main service loop"""
        self.logger.info("Main service loop started")
        
        while self.running and not self.shutdown_requested:
            try:
                if self.paused:
                    time.sleep(1)
                    continue
                
                # Calculate next update time
                next_update = self._calculate_next_update()
                
                # Wait until next update time
                while datetime.now() < next_update and self.running and not self.paused:
                    time.sleep(1)
                
                if not self.running or self.shutdown_requested:
                    break
                
                # Perform update
                self._perform_update()
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.error_count += 1
                self.last_error = str(e)
                time.sleep(5)  # Brief pause before retrying
        
        self.logger.info("Main service loop ended")
    
    def _monitor_loop(self):
        """Monitoring loop for health checks"""
        self.logger.debug("Monitor loop started")
        
        while self.running and not self.shutdown_requested:
            try:
                # Perform health checks
                self._health_check()
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.warning(f"Monitor loop error: {e}")
                time.sleep(30)
        
        self.logger.debug("Monitor loop ended")
    
    def _calculate_next_update(self) -> datetime:
        """Calculate when the next update should occur"""
        now = datetime.now()
        
        # Update at the start of each minute
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        return next_minute
    
    def _perform_update(self):
        """Perform the actual update"""
        if not self.update_callback:
            return
        
        start_time = time.time()
        
        try:
            with self.update_lock:
                self.logger.debug("Performing scheduled update")
                
                # Call the update callback
                success = self.update_callback()
                
                # Update statistics
                update_time = time.time() - start_time
                self._update_performance_stats(update_time)
                
                if success:
                    self.update_count += 1
                    self.last_update_time = datetime.now()
                    self.logger.debug(f"Update completed in {update_time:.2f}s")
                else:
                    self.error_count += 1
                    self.logger.warning("Update callback returned failure")
                
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            self.error_count += 1
            self.last_error = str(e)
    
    def _update_performance_stats(self, update_time: float):
        """Update performance statistics"""
        self.performance_stats['update_times'].append(update_time)
        
        # Keep only last 100 measurements
        if len(self.performance_stats['update_times']) > 100:
            self.performance_stats['update_times'].pop(0)
        
        # Update statistics
        times = self.performance_stats['update_times']
        self.performance_stats['avg_update_time'] = sum(times) / len(times)
        self.performance_stats['max_update_time'] = max(times)
        self.performance_stats['min_update_time'] = min(times)
    
    def _health_check(self):
        """Perform health checks"""
        try:
            # Check memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 200:  # 200MB threshold
                self.logger.warning(f"High memory usage: {memory_mb:.1f} MB")
            
            # Check if updates are happening
            if self.last_update_time:
                time_since_update = datetime.now() - self.last_update_time
                if time_since_update.total_seconds() > 300:  # 5 minutes
                    self.logger.warning(f"No updates for {time_since_update}")
            
            # Check error rate
            if self.update_count > 0:
                error_rate = self.error_count / (self.update_count + self.error_count)
                if error_rate > 0.1:  # 10% error rate
                    self.logger.warning(f"High error rate: {error_rate:.1%}")
            
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        uptime = None
        if self.start_time:
            uptime = datetime.now() - self.start_time
        
        return {
            'running': self.running,
            'paused': self.paused,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': uptime.total_seconds() if uptime else None,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'update_count': self.update_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'performance_stats': self.performance_stats.copy()
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get detailed health report"""
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            # Calculate success rate
            total_attempts = self.update_count + self.error_count
            success_rate = (self.update_count / total_attempts) if total_attempts > 0 else 0
            
            return {
                'service_health': {
                    'running': self.running,
                    'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0,
                    'success_rate': success_rate,
                    'updates_per_hour': self.update_count / ((datetime.now() - self.start_time).total_seconds() / 3600) if self.start_time else 0
                },
                'system_health': {
                    'memory_mb': memory_info.rss / 1024 / 1024,
                    'cpu_percent': cpu_percent,
                    'thread_count': threading.active_count()
                },
                'performance': self.performance_stats.copy()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate health report: {e}")
            return {'error': str(e)}
    
    def force_update(self) -> bool:
        """Force an immediate update"""
        try:
            self.logger.info("Forcing immediate update")
            self._perform_update()
            return True
        except Exception as e:
            self.logger.error(f"Force update failed: {e}")
            return False

