# 📖 Bible Clock - Enhanced Digital Scripture Display by Matt Knight

A sophisticated digital clock that displays Bible verses corresponding to the current time, featuring intelligent chapter summaries, multi-version support, voice control, and comprehensive hardware integration for Raspberry Pi.

## ✨ Features

### 🕐 **Time-Based Scripture Display**
- **Verse Mapping**: Each minute displays a corresponding Bible verse (3:16 PM shows a verse from chapter 3, verse 16)
- **Book Summaries**: At :00 minutes, displays random comprehensive summaries from all 66 Bible books
- **Smart Fallback**: Intelligent verse selection when exact matches aren't available
- **96.5% Coverage**: Extensive verse database covering most time combinations

### 📚 **Multi-Version Bible Support**
- **KJV Only Mode**: Classic King James Version display
- **KJV + Amplified Mode**: Side-by-side comparison with auto-resizing text
- **Button Toggle**: Easy switching between versions with visual feedback

### 🎮 **Three-Button Control System**
- **Button 1 (GPIO 18)**: Mode cycling (Clock ↔ Day modes)
- **Button 2 (GPIO 19)**: Bible version toggle (KJV ↔ KJV+Amplified)
- **Button 3 (GPIO 20)**: Audio/Voice activation hub

### 🔊 **Advanced Audio & Voice Features**
- **Text-to-Speech**: Reads current verse aloud with configurable voice settings
- **Wake Word Detection**: "Hey Bible" activates voice commands hands-free
- **Voice Commands**: "Explain", "Repeat", "Reference", "Mode", "Time", "Expand"
- **ChatGPT Integration**: AI-powered verse explanations and biblical insights
- **Chapter Expansion**: Voice command to display remaining verses in sequence

### 🖥️ **Intelligent Display System**
- **Auto-Resizing Text**: Dynamically adjusts font size to fit any content length
- **Temporary Mode Indicators**: Shows mode/version changes for 3 seconds
- **Cross-Platform Fonts**: Optimized for both Windows simulation and Raspberry Pi
- **E-Ink Optimization**: Designed for Waveshare 10.3" E-Ink displays

### 🔧 **Professional Hardware Integration**
- **Raspberry Pi 3B+** with optimized GPIO management
- **Waveshare 10.3" E-Ink Display HAT** with SPI configuration
- **ReSpeaker 2-Mics Pi HAT** for voice recognition
- **CQRobot 3W 4Ω Speakers** with proper amplification
- **Pimoroni HAT Hack3r** for multi-HAT compatibility
- **No-solder installation** with comprehensive wiring guides

## 🚀 Quick Start

### **Windows Testing (Simulation Mode)**

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/Jackal014/Bible-clock.git
   cd Bible-clock
   python -m venv bible_clock_env
   source bible_clock_env/Scripts/activate  # Windows Git Bash
   ```

2. **Install Dependencies**:
   ```bash
   pip install pillow>=10.0.0
   pip install python-dateutil>=2.8.2
   pip install fake-rpi>=0.7.1
   pip install tzdata>=2023.3
   pip install requests>=2.31.0
   ```

3. **Configure Environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your settings (optional for testing)
   ```

4. **Run Simulation**:
   ```bash
   python bin/run_clock.py --simulate --debug --once
   ```

### **Raspberry Pi Deployment**

1. **Hardware Setup**: Follow the comprehensive [Hardware Installation Guide](Hardware_Installation_Guide.md)

2. **Environment Configuration**: See [Environment Setup Guide](ENVIRONMENT_SETUP.md)

3. **Automated Installation**:
   ```bash
   # ReSpeaker HAT drivers
   sudo bash setup_respeaker.sh
   
   # System services and startup
   sudo bash setup_startup.sh
   
   # Hardware validation
   bash validate_hardware.sh
   ```

## 🎯 **Usage Examples**

### **Basic Operation**
```bash
# Standard operation
python bin/run_clock.py

# Simulation mode for testing
python bin/run_clock.py --simulate --debug

# Test specific time
python bin/run_clock.py --simulate --time "3:16 PM"
```

### **Testing Features**
```bash
# Test all three buttons
python bin/run_clock.py --test-buttons --simulate

# Test audio functionality
python bin/run_clock.py --test-audio --simulate

# Show system status
python bin/run_clock.py --status --simulate
```

### **Voice Commands**
After pressing Button 3 or saying "Hey Bible":
- **"Explain"** - Get AI explanation of current verse
- **"Repeat"** - Re-read the current verse
- **"Reference"** - Speak just the verse reference
- **"Expand"** - Show remaining verses in the chapter
- **"Mode"** - Announce current display mode
- **"Time"** - Announce current time

## 🔒 **Security & Privacy**

### **Environment Variables**
- **Secure Configuration**: Sensitive data (WiFi passwords, API keys) stored in `.env`
- **Git Protection**: `.env` automatically ignored by version control
- **Template System**: `.env.template` provides safe setup guide for users

### **API Key Setup**
1. Get OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Add to `.env`: `CHATGPT_API_KEY=your_actual_key_here`
3. Configure other settings as needed

## 🛠️ **Hardware Requirements**

### **Core Components**
- **Raspberry Pi 3B+** (or newer)
- **Waveshare 10.3" E-Ink Display HAT**
- **ReSpeaker 2-Mics Pi HAT**
- **CQRobot 3W 4Ω Speakers** (pair)
- **3x Momentary Push Buttons**
- **Pimoroni HAT Hack3r** (for multi-HAT setup)

### **Power & Connectivity**
- **2.5A Power Supply** (minimum)
- **MicroSD Card** (32GB+ recommended)
- **WiFi Connection** for time sync and API access

### **Optional Enhancements**
- **Safe Shutdown Button** circuit
- **Custom Enclosure** for finished appearance
- **External Antenna** for improved WiFi

## 📊 **Technical Specifications**

### **Coverage Statistics**
- **Total Time Slots**: 720 (12 hours × 60 minutes)
- **Verse Coverage**: 683 slots (94.9%)
- **Book Summary Coverage**: 12 slots (1.7%) - :00 minutes
- **Total Coverage**: 695 slots (96.5%)

### **Supported Bible Versions**
- **King James Version (KJV)**: Primary text source
- **Amplified Bible**: Side-by-side comparison mode
- **Extensible**: Framework supports additional versions

### **Audio Specifications**
- **TTS Engine**: pyttsx3 with configurable voice settings
- **Voice Recognition**: ReSpeaker 2-Mics HAT with wake word detection
- **Audio Output**: 3W speakers with proper amplification
- **Sample Rate**: 16kHz for voice recognition

## 🔧 **Configuration Options**

### **Display Settings**
```env
FONT_SIZE=80                   # Base font size
DISPLAY_WIDTH=1200             # E-ink display width
DISPLAY_HEIGHT=825             # E-ink display height
```

### **Audio Settings**
```env
TTS_VOICE_RATE=150             # Speech rate (words per minute)
TTS_VOICE_VOLUME=0.8           # Volume level (0.0-1.0)
WAKE_WORD=Hey Bible            # Custom wake word
```

### **Hardware Settings**
```env
BUTTON1_PIN=18                 # Mode button GPIO pin
BUTTON2_PIN=19                 # Version button GPIO pin
BUTTON3_PIN=20                 # Audio button GPIO pin
```

## 🧪 **Development & Testing**

### **Simulation Mode**
- **Cross-platform testing** on Windows/Mac/Linux
- **Fake GPIO** simulation for development
- **Debug output** for troubleshooting
- **Time manipulation** for testing specific verses

### **Hardware Validation**
- **Automated testing scripts** for all components
- **GPIO pin verification** and conflict detection
- **Audio system testing** with feedback
- **Display functionality** validation

## 📚 **Documentation**

- **[Hardware Installation Guide](Hardware_Installation_Guide.md)**: Complete hardware setup
- **[Environment Setup Guide](ENVIRONMENT_SETUP.md)**: Security and configuration
- **[Enhanced Features Summary](Enhanced_Features_Summary.md)**: Detailed feature overview
- **[Complete Implementation Guide](Complete_Implementation_Guide.md)**: Technical details

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/Jackal104/Bible-clock.git
cd Bible-clock

# Create development environment
python -m venv bible_clock_env
source bible_clock_env/Scripts/activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python bin/run_clock.py --test-buttons --simulate
```

## 🙏 **Acknowledgments**

- **Bible Text**: King James Version and Amplified Bible
- **Hardware**: Waveshare, ReSpeaker, Pimoroni communities
- **Libraries**: Pillow, python-dateutil, pyttsx3, and other open-source projects
- **Inspiration**: Digital scripture display and IoT maker communities

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/Jackal104/Bible-clock/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Jackal104/Bible-clock/discussions)
- **Documentation**: Check the `docs/` directory for detailed guides

---

**Built with ❤️ for digital scripture study and IoT enthusiasts**

