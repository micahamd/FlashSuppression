#!/bin/bash
# ============================================================================
# CFS Task - Build Executable Script (Linux/macOS)
# ============================================================================
# This script automates the process of building a Linux/macOS executable
# from the CFS Task Python application using PyInstaller.
# ============================================================================

echo "============================================================================"
echo "CFS Task - Build Executable (Linux/macOS)"
echo "============================================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PyInstaller is installed
echo "[1/6] Checking PyInstaller installation..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: PyInstaller is not installed.${NC}"
    echo ""
    echo "Installing PyInstaller..."
    if ! pip3 install pyinstaller; then
        echo -e "${RED}ERROR: Failed to install PyInstaller.${NC}"
        echo "Please install manually: pip3 install pyinstaller"
        exit 1
    fi
fi
echo -e "${GREEN}PyInstaller is installed. OK${NC}"
echo ""

# Verify required files exist
echo "[2/6] Verifying required files..."
MISSING_FILES=0

check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}ERROR: $1 not found${NC}"
        MISSING_FILES=1
    fi
}

check_file "display_file.py"
check_file "base_module.py"
check_file "config_file.py"
check_file "mask_file.py"
check_file "stim_file.py"
check_file "packaging_helper.py"
check_file "grey.png"
check_file "temp_checkerboard.png"
check_file "config.json"
check_file "flash_suppression_linux.spec"

if [ $MISSING_FILES -eq 1 ]; then
    echo ""
    echo -e "${RED}ERROR: Missing required files. Please ensure all files are present.${NC}"
    exit 1
fi
echo -e "${GREEN}All required files found. OK${NC}"
echo ""

# Clean previous builds
echo "[3/6] Cleaning previous build artifacts..."
if [ -d "build" ]; then
    echo "Removing build directory..."
    rm -rf build
fi
if [ -d "dist" ]; then
    echo "Removing dist directory..."
    rm -rf dist
fi
if [ -f "CFS_Task" ]; then
    echo "Removing old executable..."
    rm -f CFS_Task
fi
echo -e "${GREEN}Clean complete. OK${NC}"
echo ""

# Build executable with PyInstaller
echo "[4/6] Building executable with PyInstaller..."
echo "This may take several minutes..."
echo ""

if ! pyinstaller flash_suppression_linux.spec; then
    echo ""
    echo -e "${RED}ERROR: Build failed. Check the output above for errors.${NC}"
    exit 1
fi
echo ""
echo -e "${GREEN}Build complete. OK${NC}"
echo ""

# Verify executable was created
echo "[5/6] Verifying executable..."
if [ ! -f "dist/CFS_Task" ]; then
    echo -e "${RED}ERROR: Executable was not created at dist/CFS_Task${NC}"
    exit 1
fi

# Make executable runnable
chmod +x dist/CFS_Task
echo -e "${GREEN}Executable created successfully. OK${NC}"
echo ""

# Display file size
FILE_SIZE=$(stat -f%z "dist/CFS_Task" 2>/dev/null || stat -c%s "dist/CFS_Task" 2>/dev/null)
echo "Executable size: $FILE_SIZE bytes"
echo ""

# Create distribution package
echo "[6/6] Preparing distribution package..."
mkdir -p distribution
echo "Copying executable..."
cp dist/CFS_Task distribution/
echo "Copying README..."
cp README_DISTRIBUTION_LINUX.txt distribution/ 2>/dev/null || echo "Note: README_DISTRIBUTION_LINUX.txt not found, skipping"
echo "Copying sample directories..."
if [ -d "mask_dir_sample" ]; then
    cp -r mask_dir_sample distribution/
fi
if [ -d "stim_dir_sample" ]; then
    cp -r stim_dir_sample distribution/
fi
echo -e "${GREEN}Distribution package created in 'distribution' folder. OK${NC}"
echo ""

echo "============================================================================"
echo -e "${GREEN}BUILD SUCCESSFUL!${NC}"
echo "============================================================================"
echo ""
echo "Executable location: dist/CFS_Task"
echo "Distribution package: distribution/"
echo ""
echo "Distribution package contains:"
echo "  - CFS_Task (main executable)"
echo "  - README_DISTRIBUTION_LINUX.txt (user instructions)"
echo "  - mask_dir_sample/ (sample mask images)"
echo "  - stim_dir_sample/ (sample stimulus images)"
echo ""
echo "You can now distribute the contents of the 'distribution' folder."
echo "Users will need to provide their own complete image sets."
echo ""
echo "To run the executable:"
echo "  ./CFS_Task"
echo ""
echo "============================================================================"
