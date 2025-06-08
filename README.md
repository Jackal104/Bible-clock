# Bible Clock

## Overview

The Bible Clock is a Raspberry Pi-based application that displays Bible verses on an e-ink display with advanced features:

### Features

1. **Mode Cycling (Button 1)**
   - **Clock Mode**: Displays verses based on current time (hour = chapter, minute = verse)
   - **Day Mode**: Displays verses related to historical biblical events for the current date

2. **Version Toggle (Button 2)**
   - **KJV Only**: Displays only King James Version text
   - **KJV + Amplified**: Side-by-side display of KJV and Amplified Bible versions

3. **Improved Layout**
   - Verse text centered on screen
   - Bible reference displayed in bottom right corner
   - Mode indicator in top left (Day mode shows current date)

## Quick Start

### Basic Usage

```bash
# Run with current time (simulation mode)
python bin/run_clock.py --simulate --once

# Run continuously on Raspberry Pi
python bin/run_clock.py

# Test specific time and modes
python bin/run_clock.py --time "11:17 AM" --mode clock --version kjv_only --simulate --once
```

### Button Controls

- **Button 1**: Cycle between Clock Mode ↔ Day Mode
- **Button 2**: Toggle between KJV Only ↔ KJV + Amplified

### Command Line Options

```bash
python bin/run_clock.py [OPTIONS]

Options:
  --simulate              Run in simulation mode (no GPIO)
  --debug                 Enable debug output
  --once                  Run once and exit (for testing)
  --time TIME            Specific time to display (e.g., "2:37 PM")
  --mode {clock,day}     Set initial display mode
  --version {kjv_only,kjv_amplified}  Set initial version display
  --status               Show status information and exit
  --test-buttons         Test button functionality
```

## Features in Detail

### Clock Mode
- Uses current time to select verses
- Hour (1-12) = Bible chapter
- Minute (0-59) = Bible verse
- Randomly selects from available books with matching chapter:verse
- 96.5% time coverage (695 out of 720 possible times)

### Day Mode
- Displays verses related to historical biblical events
- Falls back to monthly events if no specific date events
- Falls back to seasonal events if no monthly events
- Covers major biblical holidays and significant dates

### Historical Events Coverage
- **30 specific dates** with biblical significance
- **12 months** with themed events
- **4 seasons** with appropriate verses
- Examples: Christmas (Dec 25), Passover (April), Creation themes (January)

### Version Display
- **KJV Only**: Clean, centered layout with verse text and reference
- **KJV + Amplified**: Side-by-side comparison with divider line
- Automatic fallback to KJV only if Amplified verse not available

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- pillow>=10.0.0
- python-dateutil>=2.8.2
- RPi.GPIO>=0.7.1 (Raspberry Pi only)
- fake-rpi>=0.7.1 (simulation)

### Font Installation
The application uses RobotoMono font, included in `assets/fonts/`

## Configuration

### Environment Variables
Create `.env` file:
```
SIMULATE=1          # 1 for simulation, 0 for Raspberry Pi
DEBUG=1             # 1 for debug output, 0 for quiet
FONT_SIZE=24        # Base font size
DISPLAY_WIDTH=1200  # Display width in pixels
DISPLAY_HEIGHT=825  # Display height in pixels
```

### Hardware Configuration
- **Button 1 (Mode)**: GPIO Pin 18 (default)
- **Button 2 (Version)**: GPIO Pin 19 (default)
- **E-ink Display**: Compatible with Waveshare displays

## File Structure

```
bible-clock/
├── bin/
│   ├── run_clock_original.py     # Original application
│   └── run_clock.py              # Main application ⭐
├── src/
│   ├── config.py                 # Configuration constants
│   ├── verse_database.py         # KJV Bible database handler
│   ├── verse_selector.py         # Time-based verse selection
│   ├── historical_events.py      # Day-based verse selection ⭐
│   ├── amplified_bible.py        # Amplified Bible support ⭐
│   ├── display.py                # Enhanced display rendering ⭐
│   ├── buttons.py                # Enhanced button controls ⭐
│   └── time_utils.py             # Time parsing utilities
├── data/
│   └── kjv.json                  # Complete KJV Bible (31,102 verses)
├── assets/fonts/
│   └── RobotoMono-Regular.ttf    # Display font
├── tests/                        # Unit tests
├── requirements.txt              # Python dependencies
├── .env                          # Environment configuration
└── README.md                     # This file
```

⭐ = New or significantly enhanced files

## Testing

### Unit Tests
```bash
python -m unittest discover tests/ -v
```

### Feature Testing
```bash
# Test button functionality
python bin/run_clock.py --test-buttons --simulate --debug

# Test different modes
python bin/run_clock.py --mode day --simulate --once
python bin/run_clock.py --mode clock --simulate --once

# Test version toggle
python bin/run_clock.py --version kjv_amplified --simulate --once

# Check application status
python bin/run_clock.py --status --simulate
```

## Deployment

### Raspberry Pi Setup
1. Install Raspberry Pi OS
2. Enable GPIO and SPI interfaces
3. Install Python dependencies
4. Connect e-ink display and buttons
5. Run: `python bin/run_clock.py`

### Simulation Mode
For development and testing on any computer:
```bash
python bin/run_clock.py --simulate --debug
```

## Troubleshooting

### Common Issues

1. **Font Loading Error**
   - Ensure RobotoMono font is in `assets/fonts/`
   - Application falls back to default font if custom font fails

2. **GPIO Errors**
   - Use `--simulate` flag for non-Raspberry Pi systems
   - Check GPIO pin connections and permissions

3. **Display Issues**
   - Verify e-ink display library installation
   - Check display dimensions in configuration

4. **Missing Verses**
   - Some time combinations don't have matching verses
   - Application provides graceful fallbacks

### Debug Mode
Enable debug output to see detailed operation:
```bash
python bin/run_clock.py --debug --simulate
```

## Statistics

### Verse Coverage
- **Total Bible Books**: 66
- **Available Times**: 695 out of 720 possible (96.5%)
- **Total Verses**: 31,102 in KJV database

### Historical Events
- **Specific Dates**: 30 events
- **Monthly Coverage**: 12 months
- **Seasonal Coverage**: 4 seasons
- **Overall Coverage**: 8.2% of calendar days with specific events

## API Reference

### BibleClock Class

```python
clock = BibleClock(simulate=True, debug=True)

# Run once
clock.run_once(target_time=datetime.now())

# Run continuously
clock.run_continuous()

# Simulate button presses
clock.simulate_button_press(1)  # Mode cycle
clock.simulate_button_press(2)  # Version toggle

# Get status
status = clock.get_status()
```

### Button Controls

```python
buttons = ButtonManager(simulate=True)
buttons.set_mode_callback(on_mode_change)
buttons.set_version_callback(on_version_change)
```

### Display Management

```python
display = DisplayManager(simulate=True)
display.display_verse(book, verse_ref, verse_text, current_time, mode, version)
```

## License

This project is for personal use. Bible text is from the King James Version (public domain) and sample Amplified Bible verses (demonstration purposes).

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run with `--debug` flag for detailed output
3. Use `--status` to check system configuration
4. Test with `--simulate` mode first

---

**Bible Clock v2.0** - Now with mode cycling, version toggle, and improved layout!

