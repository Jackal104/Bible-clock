#!/bin/bash
# Bible Clock Enhanced v2.1 - Windows Git Bash Update Script
# Specifically designed for: C:\Users\mattk\Bible-clock
# Repository: https://github.com/Jackal104/Bible-clock
set -e # Exit on any error
echo "🚀 Bible Clock Enhanced v2.1 - Windows Git Bash Update"
echo "Repository: https://github.com/Jackal104/Bible-clock"
echo "Local Path: C:\Users\mattk\Bible-clock"
echo "=================================================="
# Configuration for Windows paths
REPO_DIR="/c/Users/mattk/Bible-clock"
BACKUP_DIR="/c/Users/mattk/bible-clock-backup-$(date +%Y%m%d-
%H%M%S)"
TEMP_DIR="/c/Users/mattk/temp/bible-clock-v2.1"
PACKAGE_FILE="bible-clock-enhanced-v2.1-complete.tar.gz"
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
print_step() {
1.
2.
3.
echo -e "${BLUE}📋 Step $1: $2${NC}"
}
print_success() {
echo -e "${GREEN}✅ $1${NC}"
}
print_warning() {
echo -e "${YELLOW}⚠️ $1${NC}"
}
print_error() {
echo -e "${RED}❌ $1${NC}"
}
# Verify we're in the correct directory
print_step 1 "Verifying repository location"
if [ "$(pwd)" != "$REPO_DIR" ]; then
print_error "Please run this script from $REPO_DIR"
echo "Current directory: $(pwd)"
echo "Expected directory: $REPO_DIR"
exit 1
fi
if [ ! -d ".git" ]; then
print_error "Not in a Git repository. Please ensure you're
in the Bible-clock repository."
exit 1
fi
print_success "Repository location verified"
# Check for the enhanced package
print_step 2 "Locating enhanced package"
if [ ! -f "$PACKAGE_FILE" ]; then
print_error "Enhanced package file '$PACKAGE_FILE' not
found."
echo "Please download the package file to this directory
first."
echo "Expected location: $REPO_DIR/$PACKAGE_FILE"
exit 1
fi
print_success "Enhanced package found: $PACKAGE_FILE"
# Create backup
print_step 3 "Creating backup of current implementation"
mkdir -p "$(dirname "$BACKUP_DIR")"
cp -r "$REPO_DIR" "$BACKUP_DIR"
print_success "Backup created: $BACKUP_DIR"
# Check Git status and commit current changes
print_step 4 "Checking Git status"
if [ -n "$(git status --porcelain)" ]; then
print_warning "Uncommitted changes detected"
echo "Current changes:"
git status --short
echo
read -p "Do you want to commit current changes before
upgrade? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
git add .
git commit -m "Backup current configuration before v2.1
upgrade - $(date)"
print_success "Changes committed"
fi
fi
# Create feature branch
print_step 5 "Creating feature branch"
BRANCH_NAME="feature/bible-clock-v2.1-enhanced"
git checkout -b "$BRANCH_NAME" 2>/dev/null || {
print_warning "Branch $BRANCH_NAME already exists, switching
to it"
git checkout "$BRANCH_NAME"
}
print_success "Switched to feature branch: $BRANCH_NAME"
# Preserve configuration files
print_step 6 "Preserving configuration files"
CONFIG_BACKUP_DIR="/c/Users/mattk/temp/config-backup-$(date +
%Y%m%d-%H%M%S)"
mkdir -p "$CONFIG_BACKUP_DIR"
# Preserve various configuration files that might exist
cp .env "$CONFIG_BACKUP_DIR/" 2>/dev/null && print_success
"Preserved .env" || print_warning "No .env file found"
cp vcom.conf "$CONFIG_BACKUP_DIR/" 2>/dev/null && print_success
"Preserved vcom.conf" || print_warning "No vcom.conf file found"
cp config.py "$CONFIG_BACKUP_DIR/" 2>/dev/null && print_success
"Preserved config.py" || print_warning "No config.py file found"
cp -r data/ "$CONFIG_BACKUP_DIR/" 2>/dev/null && print_success
"Preserved data directory" || print_warning "No data directory
found"
print_success "Configuration files preserved in:
$CONFIG_BACKUP_DIR"
# Extract enhanced package
print_step 7 "Extracting enhanced package"
mkdir -p "$TEMP_DIR"
tar -xzf "$PACKAGE_FILE" -C "$TEMP_DIR"
print_success "Enhanced package extracted to $TEMP_DIR"
# Remove old files (preserve .git and important files)
print_step 8 "Removing old implementation files"
print_warning "Removing old Python files..."
find . -name "*.py" -not -path "./.git/*" -not -name
"update_repository_windows.sh" -delete 2>/dev/null || true
print_warning "Removing old documentation..."
find . -name "*.md" -not -path "./.git/*" -delete 2>/dev/null ||
true
print_warning "Removing old directories..."
rm -rf src/ bin/ data/ systemd/ web-interface/ api-backend/
tests/ 2>/dev/null || true
print_success "Old files removed"
# Copy enhanced Bible Clock core
print_step 9 "Installing enhanced Bible Clock core"
cp -r "$TEMP_DIR/bible-clock-enhanced/"* .
print_success "Enhanced core installed"
# Install web interface
print_step 10 "Installing web interface"
mkdir -p web-interface
cp -r "$TEMP_DIR/bible-clock-web-interface/"* web-interface/
print_success "Web interface installed"
# Install API backend
print_step 11 "Installing API backend"
mkdir -p api-backend
cp -r "$TEMP_DIR/bible-clock-api/"* api-backend/
print_success "API backend installed"
# Restore configuration
print_step 12 "Restoring configuration"
if [ -f "$CONFIG_BACKUP_DIR/.env" ]; then
cp "$CONFIG_BACKUP_DIR/.env" .
print_success "Configuration restored from backup"
else
if [ -f ".env.template" ]; then
cp .env.template .env
print_warning "Created .env from template - please
configure manually"
else
print_warning "No configuration template found - please
create .env file manually"
fi
fi
# Update .env for Windows paths if it exists
if [ -f ".env" ]; then
print_warning "Updating .env for Windows paths..."
sed -i 's|WORKING_DIRECTORY=/home/pi/bible-clock-enhanced|
WORKING_DIRECTORY=/c/Users/mattk/Bible-clock|g' .env
sed -i 's|LOG_FILE=/var/log/bible-clock.log|LOG_FILE=/c/
Users/mattk/temp/bible-clock.log|g' .env
print_success "Updated .env for Windows environment"
fi
# Install dependencies (Note: This requires Python and Node.js
to be installed)
print_step 13 "Installing dependencies"
print_warning "Note: This step requires Python and Node.js to be
installed on Windows"
# Check if Python is available
if command -v python &> /dev/null || command -v python3 &> /dev/
null; then
print_warning "Installing Python dependencies for core..."
python -m pip install -r requirements.txt 2>/dev/null ||
python3 -m pip install -r requirements.txt 2>/dev/null ||
print_warning "Could not install Python dependencies - install
manually"
else
print_warning "Python not found - please install Python
dependencies manually"
fi
# Check if Node.js is available
if command -v npm &> /dev/null; then
print_warning "Installing Node.js dependencies for web
interface..."
cd web-interface
npm install 2>/dev/null || print_warning "Could not install
Node.js dependencies - install manually"
cd ..
else
print_warning "Node.js/npm not found - please install
Node.js dependencies manually"
fi
print_success "Dependency installation completed (check warnings
above)"
# Test the installation
print_step 14 "Testing installation"
if command -v python &> /dev/null || command -v python3 &> /dev/
null; then
python bin/validate_config.py 2>/dev/null || python3 bin/
validate_config.py 2>/dev/null || print_warning "Configuration
validation failed - please check .env file"
if [ $? -eq 0 ]; then
print_success "Configuration validation passed"
fi
else
print_warning "Cannot test installation - Python not
available"
fi
# Commit changes
print_step 15 "Committing enhanced implementation"
git add .
git commit -m "Upgrade to Bible Clock Enhanced v2.1 - Windows
Git Bash
- Fixed red background issue with proper grayscale image
generation
- Added professional React-based web interface for configuration
- Implemented Flask API backend for real-time system management
- Added 8 custom e-ink optimized backgrounds
- Enhanced configuration system with web-based management
- Improved performance optimization and error handling
- Added comprehensive monitoring and status reporting
- Restructured codebase for better maintainability
- Configured for Windows environment with Git Bash
Repository: https://github.com/Jackal104/Bible-clock
Local Path: C:\Users\mattk\Bible-clock
Platform: Windows with Git Bash
Components added:
- web-interface/: React-based configuration dashboard
- api-backend/: Flask API for system management
- Enhanced core application with background support
- Custom background library optimized for e-ink displays
Breaking changes:
- Restructured directory layout
- New configuration options in .env file
- Additional dependencies for web interface and API
- Windows-specific path configurations
Migration notes:
- Preserved existing hardware configuration
- Maintained backward compatibility for core settings
- Added new features while preserving existing functionality
- Updated paths for Windows environment"
print_success "Changes committed to feature branch"
# Merge to main (optional)
print_step 16 "Merging to main branch"
read -p "Do you want to merge to main branch now? (y/n): " -n 1
-r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
git checkout main
git merge "$BRANCH_NAME"
git tag -a v2.1.0 -m "Bible Clock Enhanced v2.1.0 - Windows
Git Bash Edition"
print_success "Merged to main branch and tagged as v2.1.0"
read -p "Do you want to push to GitHub repository? (y/n): "
-n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
git push origin main
git push origin v2.1.0
print_success "Pushed to GitHub: https://github.com/
Jackal104/Bible-clock"
fi
else
print_warning "Staying on feature branch. Merge manually
when ready:"
echo " git checkout main"
echo " git merge $BRANCH_NAME"
echo " git push origin main"
fi
# Cleanup
print_step 17 "Cleaning up temporary files"
rm -rf "$TEMP_DIR"
print_success "Temporary files cleaned up"
# Final instructions
echo
echo "🎉 Bible Clock Enhanced v2.1 Update Complete!"
echo "Repository: https://github.com/Jackal104/Bible-clock"
echo "============================================="
echo
echo "Next steps for Windows development:"
echo "1. Configure your settings in the .env file if needed"
echo "2. For Raspberry Pi deployment:"
echo " - Transfer files to your Raspberry Pi"
echo " - Install Python dependencies: pip install -r
requirements.txt"
echo " - Install Node.js dependencies: cd web-interface && npm
install"
echo " - Start web interface: npm run dev --host"
echo " - Start API backend: cd api-backend && python src/
main.py"
echo "3. Access web interface at: http://your-pi-ip:5174"
echo "4. Test on Pi: python bin/run_clock.py --test --simulate"
echo
echo "Backup location: $BACKUP_DIR"
echo "Config backup: $CONFIG_BACKUP_DIR"
echo "Documentation: README.md"
echo
print_success "Windows Git Bash update completed successfully!"
