================================================================================
        BREAKING CONTINUOUS FLASH SUPPRESSION (b-CFS) TASK
                     Windows Executable Distribution
================================================================================

QUICK START GUIDE
================================================================================

1. LAUNCH THE APPLICATION
   - Double-click "CFS_Task.exe" to start the application
   - The configuration window will appear

2. SELECT IMAGE DIRECTORIES
   - Click "Browse" next to "Select Mask Directory"
     > Choose a folder containing your mask images (Mondrian patterns)
     > Sample folder included: "mask_dir_sample" (for testing only)
   
   - Click "Browse" next to "Select Stimulus Directory"
     > Choose a folder containing your stimulus images
     > Sample folder included: "stim_dir_sample" (for testing only)
   
   - Your directory selections will be saved and remembered for future runs

3. CONFIGURE EXPERIMENT PARAMETERS
   - Set the number of trials
   - Adjust timing parameters (stimulus duration, mask refresh rate)
   - Configure suppressor position (or use practice mode to determine it)
   - Set participant ID for data tracking

4. START THE EXPERIMENT
   - Click "Start Task" to begin the main experiment
   - OR click "Practice?" checkbox first to run practice mode (recommended)

5. DURING THE EXPERIMENT
   - SPACE: Start trial / Stop stimulus presentation
   - 'a' key: Respond that stimulus appeared in TOP position
   - 'z' key: Respond that stimulus appeared in BOTTOM position
   - 'q' key: Quit current task and return to configuration (saves data)

6. DATA OUTPUT
   - "trial_data.csv" - Main experiment data
   - "practice_trial_data.csv" - Practice trial data (if practice mode used)
   - Files are saved in the same folder as CFS_Task.exe

================================================================================
SYSTEM REQUIREMENTS
================================================================================

Operating System: Windows 10 or later (64-bit)
Memory (RAM):     4GB minimum, 8GB recommended
Display:          1280x800 resolution or higher
Storage:          100MB free space for application and data
Additional:       Stereoscope or mirror apparatus for binocular viewing

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

Q: Application won't start or shows error
A: Ensure Windows Defender or antivirus isn't blocking it. Try running as
   administrator or add exception for CFS_Task.exe.

Q: "No image files found" error
A: Verify your mask/stimulus directories contain PNG or JPG images.
   Check that you browsed to the correct folders.

Q: Data files aren't being created
A: Ensure the folder containing CFS_Task.exe has write permissions.
   Try running from a folder in your Documents or Desktop.

Q: Images don't display correctly
A: Check image dimensions. Masks should be 640x800, stimuli 200x300.
   Ensure images are in RGB or RGBA color mode.

Q: Application is slow or laggy
A: Reduce number of mask images in your mask directory. Increase the
   mask cycle time. Close other applications to free up RAM.

Q: Can't exit the application
A: Press 'q' during experiment to return to config window, then click
   "Exit" button. Or use Alt+F4 to force close.

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
Version: 1.0
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
