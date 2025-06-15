# Bible Clock Enhanced - Complete Working Package

**Version:** 2.0 Enhanced Edition  
**Date:** June 15, 2025  
**Author:** Manus AI  

## Overview

Bible Clock Enhanced is a comprehensive, production-ready implementation of a Bible verse display system for Raspberry Pi with e-ink displays. This enhanced version incorporates all the lessons learned from the original setup guide and provides a robust, feature-rich solution with advanced optimizations, error handling, and monitoring capabilities.

## Key Features

### 🚀 **Enhanced Performance**
- **Optimized Display Refresh**: Intelligent change detection to minimize unnecessary refreshes
- **Memory Management**: Automatic garbage collection and memory monitoring
- **Caching System**: API response caching to reduce network requests
- **Performance Tracking**: Detailed performance metrics and statistics

### 🛡️ **Robust Error Handling**
- **Graceful Degradation**: Fallback to local verses when API is unavailable
- **Automatic Recovery**: Service auto-restart on failures
- **Comprehensive Logging**: Detailed logging with rotation and monitoring
- **Health Monitoring**: Continuous health checks and alerting

### 🔧 **Advanced Configuration**
- **Environment-based Config**: Flexible configuration via environment variables
- **Hardware Abstraction**: Support for both hardware and simulation modes
- **Validation System**: Comprehensive configuration validation
- **Hot Reloading**: Configuration updates without service restart

### 📊 **Monitoring & Management**
- **Service Management**: Systemd integration with proper lifecycle management
- **Performance Monitoring**: Real-time performance and resource monitoring
- **Status Dashboard**: Comprehensive status reporting and diagnostics
- **Maintenance Tools**: Automated maintenance and backup scripts

### 🎨 **Enhanced Display**
- **Intelligent Layout**: Responsive layout that adapts to content
- **Font Management**: Advanced font loading with fallbacks
- **Time-based Themes**: Different verse selections based on time of day
- **Special Verses**: Highlighted verses for significant times (3:16, 23:1, etc.)

## Project Structure

```
bible-clock-enhanced/
├── bin/                          # Executable scripts
│   ├── run_clock.py             # Main application entry point
│   ├── validate_config.py       # Configuration validation
│   ├── test_fallback.py         # Fallback testing utility
│   └── monitor_service.sh       # Service monitoring script
├── src/                          # Source code modules
│   ├── config.py                # Enhanced configuration management
│   ├── bible_api.py             # Bible API with caching and fallback
│   ├── verse_manager.py         # Intelligent verse selection
│   ├── image_generator.py       # Optimized image generation
│   ├── display.py               # Display management with error handling
│   ├── waveshare_wrapper.py     # Optimized Waveshare driver wrapper
│   └── service_manager.py       # Service lifecycle management
├── data/                         # Data files
│   ├── fonts/                   # Font files (TTF)
│   └── fallback_verses.json    # Offline verse database
├── systemd/                      # System service files
│   └── bible-clock.service     # Systemd service definition
├── tests/                        # Test files
├── requirements.txt             # Python dependencies
├── .env.template               # Environment configuration template
├── install.sh                  # Installation script
└── README.md                   # This file
```

## Installation

### Prerequisites

- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (64-bit recommended)
- Python 3.7 or newer
- Internet connection for initial setup
- Waveshare IT8951 e-ink display HAT (for hardware mode)

### Quick Installation

1. **Download and extract** the Bible Clock Enhanced package to your Raspberry Pi
2. **Run the installation script**:
   ```bash
   cd bible-clock-enhanced
   ./install.sh
   ```
3. **Configure your settings**:
   ```bash
   nano .env
   ```
4. **Test the installation**:
   ```bash
   python bin/run_clock.py --test
   ```
5. **Start the service**:
   ```bash
   sudo systemctl start bible-clock.service
   ```

### Manual Installation

If you prefer manual installation or need to customize the process:

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip git
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your specific settings
   ```

5. **Validate configuration**:
   ```bash
   python bin/validate_config.py
   ```

## Configuration

### Environment Variables

The application is configured via environment variables in the `.env` file:

#### Display Configuration
```bash
DISPLAY_WIDTH=1872              # Display width in pixels
DISPLAY_HEIGHT=1404             # Display height in pixels
DISPLAY_TYPE=IT8951             # Display controller type
VCOM_VALUE=-1.50               # Display VCOM value
```

#### Bible API Configuration
```bash
BIBLE_API_URL=https://bible-api.com  # Bible API endpoint
BIBLE_VERSION=kjv                    # Bible version (KJV)
FALLBACK_ENABLED=true               # Enable fallback verses
```

#### Performance Configuration
```bash
MEMORY_LIMIT_MB=100             # Memory usage limit
REFRESH_OPTIMIZATION=true      # Enable display optimizations
FULL_REFRESH_INTERVAL=10       # Full refresh every N updates
```

#### Simulation Mode
```bash
SIMULATION_MODE=false           # Enable for testing without hardware
```

### Hardware Configuration

For hardware installations, ensure:

1. **SPI is enabled**:
   ```bash
   sudo raspi-config nonint do_spi 0
   ```

2. **Driver is installed** and accessible at the configured path
3. **VCOM value is correct** for your specific display panel
4. **Permissions are set** for GPIO and SPI access

## Usage

### Running the Application

#### As a Service (Recommended)
```bash
# Start the service
sudo systemctl start bible-clock.service

# Enable auto-start on boot
sudo systemctl enable bible-clock.service

# Monitor the service
./bin/monitor_service.sh
```

#### Manual Execution
```bash
# Run once and exit
python bin/run_clock.py --once

# Run in debug mode
python bin/run_clock.py --debug

# Run in simulation mode
python bin/run_clock.py --simulate
```

#### Testing and Validation
```bash
# Validate configuration
python bin/validate_config.py

# Run component tests
python bin/run_clock.py --test

# Test with fallback data
python bin/test_fallback.py

# Check application status
python bin/run_clock.py --status
```

### Monitoring and Maintenance

#### Service Monitoring
```bash
# Check service status
./bin/monitor_service.sh

# View logs
sudo journalctl -u bible-clock.service -f

# Check resource usage
htop -p $(pgrep -f run_clock.py)
```

#### Performance Monitoring
The application provides built-in performance monitoring:
- Memory usage tracking
- Display refresh timing
- API response times
- Error rate monitoring
- Cache hit rates

## Troubleshooting

### Common Issues

#### 1. Display Not Working
- **Check connections**: Ensure all ribbon cables are properly connected
- **Verify VCOM**: Confirm VCOM value matches your display panel
- **Test driver**: Run the official Waveshare demo to verify hardware
- **Check permissions**: Ensure user has access to SPI and GPIO

#### 2. Service Won't Start
- **Check logs**: `sudo journalctl -u bible-clock.service -n 50`
- **Validate config**: `python bin/validate_config.py`
- **Check dependencies**: Ensure all Python packages are installed
- **Verify paths**: Confirm all file paths in configuration are correct

#### 3. API Rate Limiting
- **Enable fallback**: Set `FALLBACK_ENABLED=true` in `.env`
- **Check cache**: API responses are cached to reduce requests
- **Use local data**: Fallback verses work offline

#### 4. Memory Issues
- **Monitor usage**: Use built-in memory monitoring
- **Adjust limits**: Modify `MEMORY_LIMIT_MB` in configuration
- **Check for leaks**: Review logs for memory warnings

### Debug Mode

Enable debug mode for detailed troubleshooting:
```bash
# Set in .env file
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Or run with debug flag
python bin/run_clock.py --debug
```

### Simulation Mode

Test without hardware using simulation mode:
```bash
# Set in .env file
SIMULATION_MODE=true

# Or run with simulate flag
python bin/run_clock.py --simulate
```

Generated images are saved to `/tmp/bible_clock_display_*.png` for inspection.

## Advanced Features

### Custom Verse Selection

The application includes intelligent verse selection based on:
- **Time of day**: Different books preferred for morning, afternoon, evening
- **Special times**: Highlighted verses for significant times (John 3:16, Psalm 23:1)
- **Fallback system**: Local verses when API is unavailable
- **Randomization**: Variety in verse selection while maintaining time correlation

### Performance Optimization

- **Change Detection**: Only refresh display when content changes
- **Memory Management**: Automatic garbage collection and monitoring
- **Caching**: API responses cached to reduce network load
- **Resource Limits**: Configurable memory and CPU limits

### Monitoring and Alerting

- **Health Checks**: Continuous monitoring of service health
- **Performance Metrics**: Detailed performance tracking and reporting
- **Error Recovery**: Automatic recovery from common failure modes
- **Log Management**: Automatic log rotation and cleanup

## Development

### Adding New Features

The modular architecture makes it easy to extend functionality:

1. **New verse sources**: Extend `BibleAPI` class
2. **Custom layouts**: Modify `ImageGenerator` class  
3. **Additional displays**: Extend `DisplayManager` class
4. **New monitoring**: Add to `ServiceManager` class

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python bin/test_fallback.py

# Component tests
python bin/run_clock.py --test
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

### Documentation
- **Setup Guide**: See the complete setup guide for detailed installation instructions
- **API Reference**: Code is thoroughly documented with docstrings
- **Configuration**: All configuration options are documented in `.env.template`

### Community
- **Issues**: Report bugs and request features via GitHub issues
- **Discussions**: Join community discussions for help and ideas
- **Wiki**: Additional documentation and examples

## License

This project is released under the MIT License. See LICENSE file for details.

## Acknowledgments

- **Waveshare**: For excellent e-ink display hardware and drivers
- **Bible API**: For providing free access to Bible verses
- **Raspberry Pi Foundation**: For the amazing Raspberry Pi platform
- **Community**: For feedback, testing, and contributions

---

**Bible Clock Enhanced** - Bringing timeless wisdom to modern displays.

