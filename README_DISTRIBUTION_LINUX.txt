================================================================================
        BREAKING CONTINUOUS FLASH SUPPRESSION (b-CFS) TASK
                     Linux/macOS Executable Distribution
================================================================================

QUICK START GUIDE
================================================================================

1. MAKE THE APPLICATION EXECUTABLE
   - Open terminal in the folder containing CFS_Task
   - Run: chmod +x CFS_Task
   - (This step only needs to be done once)

2. LAUNCH THE APPLICATION
   - In terminal: ./CFS_Task
   - Or: Double-click CFS_Task (if your file manager supports it)
   - The configuration window will appear

3. SELECT IMAGE DIRECTORIES
   - Click "Browse" next to "Select Mask Directory"
     > Choose a folder containing your mask images (Mondrian patterns)
     > Sample folder included: "mask_dir_sample" (for testing only)
   
   - Click "Browse" next to "Select Stimulus Directory"
     > Choose a folder containing your stimulus images
     > Sample folder included: "stim_dir_sample" (for testing only)
   
   - Your directory selections will be saved and remembered for future runs

4. CONFIGURE EXPERIMENT PARAMETERS
   - Set the number of trials
   - Adjust timing parameters (stimulus duration, mask refresh rate)
   - Configure suppressor position (or use practice mode to determine it)
   - Set participant ID for data tracking

5. START THE EXPERIMENT
   - Click "Start Task" to begin the main experiment
   - OR click "Practice?" checkbox first to run practice mode (recommended)

6. DURING THE EXPERIMENT
   - SPACE: Start trial / Stop stimulus presentation
   - 'a' key: Respond that stimulus appeared in TOP position
   - 'z' key: Respond that stimulus appeared in BOTTOM position
   - 'q' key: Quit current task and return to configuration (saves data)

7. DATA OUTPUT
   - "trial_data.csv" - Main experiment data
   - "practice_trial_data.csv" - Practice trial data (if practice mode used)
   - Files are saved in the same folder as CFS_Task

================================================================================
SYSTEM REQUIREMENTS
================================================================================

Operating System: Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+) or macOS 11+
Python:           Not required (bundled in executable)
Display Server:   X11 or Wayland with XWayland
Memory (RAM):     4GB minimum, 8GB recommended
Display:          1280x800 resolution or higher
Storage:          100MB free space for application and data
Additional:       Stereoscope or mirror apparatus for binocular viewing

LINUX DEPENDENCIES:
The executable includes Python and most libraries, but may require:
- Tkinter system libraries: python3-tk (usually pre-installed)
- X11 libraries: libX11, libxcb
- If missing, install with:
  Ubuntu/Debian: sudo apt-get install python3-tk libx11-6
  Fedora:        sudo dnf install python3-tkinter libX11
  Arch:          sudo pacman -S tk

================================================================================
IMAGE REQUIREMENTS
================================================================================

MASK IMAGES (Mondrian Patterns):
- Format: PNG or JPG
- Recommended size: 640x800 pixels
- Suggested quantity: 10-100 different masks
- Purpose: Creates suppression effect through rapid cycling

STIMULUS IMAGES:
- Format: PNG or JPG
- Recommended size: 200x300 pixels
- Suggested quantity: 8-50 different stimuli
- Purpose: Target images that participants detect

NOTE: Sample directories (mask_dir_sample and stim_dir_sample) contain
      only 3 images each - FOR TESTING ONLY. Use your own complete image
      sets for actual experiments.

================================================================================
RUNNING THE APPLICATION
================================================================================

TERMINAL METHOD (Recommended):
1. Open terminal
2. Navigate to application folder: cd /path/to/CFS_Task/folder
3. Make executable (first time only): chmod +x CFS_Task
4. Run: ./CFS_Task

FILE MANAGER METHOD:
1. Navigate to application folder in file manager
2. Right-click CFS_Task → Properties → Permissions
3. Check "Allow executing file as program" or similar
4. Double-click CFS_Task to launch

TROUBLESHOOTING LAUNCH ISSUES:
If executable won't run, try:
  chmod +x CFS_Task
  ./CFS_Task

If you see "Permission denied":
  sudo chmod +x CFS_Task

If you see "No such file or directory" but file exists:
  This may indicate missing 32-bit libraries on 64-bit system
  The executable is 64-bit and should work on modern Linux

================================================================================
IMPORTANT NOTES
================================================================================

FIRST RUN:
- On first launch, you MUST select directories for masks and stimuli
- Use the sample directories for initial testing
- Replace with your own complete image sets before running experiments

DATA PERSISTENCE:
- Your directory selections are saved in "config_ui_settings.json"
- Experiment parameters are saved in "config.json"
- These files are created automatically in the same folder as the executable

DATA MANAGEMENT:
- Each participant's data is saved with their unique Participant ID
- Use "Clear Data" button to reset between participants
- Or manually rename CSV files to preserve previous data
- Example: "trial_data.csv" → "trial_data_P001.csv"

FILE PERMISSIONS:
- The executable needs write permission in its directory (for data files)
- If you place it in a system directory, run from a writeable location
- Best practice: Keep in user's home directory or Documents folder

DISPLAY SERVER:
- Works with X11 and Wayland (with XWayland)
- Tkinter-based GUI should work on most Linux distributions
- If GUI issues occur, ensure X11/XWayland is available

STEREOSCOPIC DISPLAY:
- This application requires a stereoscope or mirror apparatus
- Each half of the screen presents to a different eye
- Ensure proper alignment and viewing distance for your setup

PRACTICE MODE (RECOMMENDED):
- Runs 20 trials with alternating suppressor positions
- Automatically calculates non-dominant eye
- Sets optimal suppressor position for main experiment
- Results displayed after completion

================================================================================
TROUBLESHOOTING
================================================================================

Q: Application won't start
A: 1. Check permissions: chmod +x CFS_Task
   2. Check for missing libraries: ldd CFS_Task
   3. Install python3-tk if needed: sudo apt-get install python3-tk
   4. Try running from terminal to see error messages: ./CFS_Task

Q: "No image files found" error
A: Verify your mask/stimulus directories contain PNG or JPG images.
   Check that you browsed to the correct folders.

Q: Data files aren't being created
A: Ensure the folder containing CFS_Task has write permissions.
   Try running from your home directory or Documents folder.

Q: Images don't display correctly
A: Check image dimensions. Masks should be 640x800, stimuli 200x300.
   Ensure images are in RGB or RGBA color mode.

Q: Application is slow or laggy
A: Reduce number of mask images in your mask directory. Increase the
   mask cycle time. Close other applications to free up RAM.

Q: GUI looks weird or doesn't render properly
A: Ensure X11 or XWayland is available. Try setting:
   export GDK_BACKEND=x11
   Then run: ./CFS_Task

Q: Can't exit the application
A: Press 'q' during experiment to return to config window, then click
   "Exit" button. Or press Ctrl+C in terminal if launched that way.

================================================================================
BUILDING FROM SOURCE (OPTIONAL)
================================================================================

If you want to build the executable yourself on Linux:

1. Install dependencies:
   sudo apt-get install python3 python3-pip python3-tk  # Ubuntu/Debian
   sudo dnf install python3 python3-pip python3-tkinter  # Fedora

2. Install Python packages:
   pip3 install -r requirements.txt
   pip3 install pyinstaller

3. Build executable:
   chmod +x build_executable_linux.sh
   ./build_executable_linux.sh

   Or manually:
   pyinstaller flash_suppression_linux.spec

4. Find executable at: dist/CFS_Task

================================================================================
PLATFORM-SPECIFIC NOTES
================================================================================

UBUNTU/DEBIAN:
- Should work out of the box on Ubuntu 20.04+
- Install python3-tk if GUI doesn't appear: sudo apt-get install python3-tk

FEDORA/RHEL:
- Install tkinter: sudo dnf install python3-tkinter
- May need libX11: sudo dnf install libX11

ARCH LINUX:
- Install tk: sudo pacman -S tk
- Should work on recent Arch installations

macOS:
- Works on macOS 11 (Big Sur) and later
- Requires XQuartz for X11 support if not using native Aqua Tk
- Launch from terminal or by double-clicking

================================================================================
SUPPORT & DOCUMENTATION
================================================================================

For complete documentation, see the full README.md file.

For questions, bug reports, or feature requests:
- GitHub: https://github.com/micahamd/FlashSuppression
- Issues: https://github.com/micahamd/FlashSuppression/issues

================================================================================
VERSION INFORMATION
================================================================================

Application: CFS Task
Version: 1.0 (Linux/macOS)
Build Date: October 2025
Author: Micah Amd
License: [See LICENSE file]

================================================================================
CITATION
================================================================================

If you use this software in research, please cite:

Amd, M. (2024). Breaking continuous flash suppression: A psychophysical 
paradigm for investigating visual awareness. Journal of Vision.

GitHub repository: https://github.com/micahamd/FlashSuppression

================================================================================
                            END OF DOCUMENTATION
================================================================================
