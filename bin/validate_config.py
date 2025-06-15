#!/usr/bin/env python3
"""
Configuration Validation Script

This script validates the Bible Clock configuration and environment
to ensure all components are properly set up.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def validate_config():
    """Validate Bible Clock configuration"""
    errors = []
    warnings = []
    
    print("=== Bible Clock Configuration Validation ===")
    
    # Check Python version
    if sys.version_info < (3, 7):
        errors.append(f"Python 3.7+ required, found {sys.version}")
    else:
        print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check required Python packages
    required_packages = ['PIL', 'requests', 'psutil']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ Package {package}: Available")
        except ImportError:
            errors.append(f"Missing Python package: {package}")
    
    # Check configuration module
    try:
        from config import config
        print("✓ Configuration module: Loaded")
        
        # Validate configuration
        validation = config.validate_config()
        if validation['valid']:
            print("✓ Configuration: Valid")
        else:
            errors.extend(validation['errors'])
        
        warnings.extend(validation['warnings'])
        
    except ImportError as e:
        errors.append(f"Failed to import configuration: {e}")
    
    # Check driver availability (if not in simulation mode)
    try:
        from config import config
        if not config.SIMULATION_MODE:
            driver_path = Path(config.DRIVER_PATH)
            if driver_path.exists():
                if os.access(driver_path, os.X_OK):
                    print(f"✓ Driver executable: {driver_path}")
                else:
                    errors.append(f"Driver not executable: {driver_path}")
            else:
                errors.append(f"Driver not found: {driver_path}")
        else:
            print("✓ Simulation mode: Driver check skipped")
    except Exception as e:
        warnings.append(f"Driver check failed: {e}")
    
    # Check SPI interface (if not in simulation mode)
    try:
        from config import config
        if not config.SIMULATION_MODE:
            spi_devices = ["/dev/spidev0.0", "/dev/spidev0.1"]
            spi_available = any(Path(dev).exists() for dev in spi_devices)
            if spi_available:
                print("✓ SPI interface: Available")
            else:
                errors.append("SPI interface not enabled")
        else:
            print("✓ Simulation mode: SPI check skipped")
    except Exception as e:
        warnings.append(f"SPI check failed: {e}")
    
    # Check VCOM configuration
    try:
        from config import config
        vcom_file = Path(config.VCOM_CONFIG_FILE)
        if vcom_file.exists():
            print(f"✓ VCOM configuration: {vcom_file}")
        else:
            warnings.append(f"VCOM configuration not found: {vcom_file}")
    except Exception as e:
        warnings.append(f"VCOM check failed: {e}")
    
    # Check font directory
    try:
        from config import config
        font_path = Path(config.FONT_PATH)
        if font_path.exists():
            font_files = list(font_path.glob("*.ttf"))
            if font_files:
                print(f"✓ Fonts: {len(font_files)} TTF files found")
            else:
                warnings.append("No TTF font files found")
        else:
            warnings.append(f"Font directory not found: {font_path}")
    except Exception as e:
        warnings.append(f"Font check failed: {e}")
    
    # Check log directory
    try:
        from config import config
        log_file = Path(config.LOG_FILE)
        log_dir = log_file.parent
        if log_dir.exists():
            print(f"✓ Log directory: {log_dir}")
        else:
            warnings.append(f"Log directory does not exist: {log_dir}")
    except Exception as e:
        warnings.append(f"Log directory check failed: {e}")
    
    # Print results
    print("\n=== Validation Results ===")
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  ⚠ {warning}")
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  ✗ {error}")
        print("\nConfiguration validation FAILED")
        return False
    else:
        print("✓ Configuration validation PASSED")
        return True


if __name__ == "__main__":
    success = validate_config()
    sys.exit(0 if success else 1)

