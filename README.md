# Breaking Continuous Flash Suppression (b-CFS) Task

## Overview

This Breaking Continuous Flash Suppression (b-CFS) task, described in Amd (2024), is a psychophysical paradigm used to investigate visual awareness and unconscious processing. The task presents a target stimulus to one eye while dynamic Mondrian masks are presented to the other eye. This creates interocular suppression, where the target stimulus is initially invisible to the observer but gradually breaks through into awareness.

## Key Features

- **Binocular Rivalry**: Presents different stimuli to each eye to create interocular suppression
- **Flexible Alpha Transitions**: Stimuli can fade in (invisible→visible) or fade out (visible→invisible) with fine-grained control (0.00 to 0.99 alpha)
- **Eye Dominance Testing**: Optional practice mode with alternating suppressor positions to determine eye dominance
- **Extensive Configurability**: Customize timing, presentation, visual parameters, and inter-trial messaging
- **Independent Operation Modes**: Run practice trials and main task independently or sequentially
- **Comprehensive Data Collection**: Records reaction times, accuracy, suppressor positions, and trial metadata
- **Intuitive Exit Controls**: Clear distinction between task termination and application exit

## Project Structure

### Core Files

- **`display_file.py`**: Main application entry point and display coordinator
  - Manages the overall experiment flow and trial sequence
  - Handles key press events and user interactions
  - Coordinates the mask and stimulus modules
  - Implements the suppressor switching functionality
  - Manages data collection and storage
  - Controls application exit and task termination logic

- **`config_file.py`**: Configuration interface and settings management
  - Provides a comprehensive GUI for experiment configuration
  - Validates user inputs and saves configuration to JSON
  - Implements practice mode sequence generation (5L5R5L5R or 5R5L5R5L)
  - Handles non-dominant eye calculation and display after practice
  - Manages participant ID assignment
  - Controls alpha transition direction (normal or reverse)

- **`base_module.py`**: Base class for visual presentation modules
  - Defines common functionality for visual modules
  - Handles image loading and processing
  - Manages canvas creation and checkerboard border drawing
  - Provides customizable inter-trial interval messaging
  - Loads configuration settings for all visual modules

- **`stim_file.py`**: Target stimulus presentation module
  - Controls the gradual alpha blending of target stimuli (0.00 → 0.99 or reverse)
  - Supports bidirectional alpha transitions (fade-in or fade-out)
  - Manages stimulus positioning (top/bottom randomization)
  - Handles reaction time measurement from stimulus onset
  - Processes user responses during stimulus presentation
  - Implements smooth 50ms update intervals for fluid transitions

- **`mask_file.py`**: Dynamic mask presentation module
  - Implements the Mondrian mask cycling at configurable rates
  - Controls mask refresh rate and timing (independent of stimulus alpha)
  - Manages the suppression effect through rapid image cycling
  - Maintains fixation point visibility throughout presentation

### Data and Configuration Files

- **`config.json`**: Stores the current experiment configuration including all customizable parameters
- **`trial_data.csv`**: Contains data from the main experimental trials with participant ID
- **`practice_trial_data.csv`**: Contains data from practice trials for dominance calculation
- **`temp_main_config.json`**: Temporary storage for configuration between practice and main task

### Resource Directories

- **`mask_dir/`**: Directory containing Mondrian mask images (640x800 pixels recommended)
- **`stim_dir/`**: Directory containing target stimulus images (200x300 pixels recommended)

## Detailed Functionality

### Practice Mode (Optional)

The practice mode is designed to help determine the participant's non-dominant eye, but is **not required** to run the main task:

1. **Automatic Sequence Generation**: Randomly selects 5L5R5L5R or 5R5L5R5L pattern
2. **20 Trial Session**: Presents 20 trials with automatic suppressor switching at trials 5, 10, and 15
3. **Accuracy-Based Analysis**: Calculates reaction times for each eye configuration using only accurate responses
4. **Block Analysis**: Skips the first trial of each 5-trial block (analyzes 8 trials per side)
5. **Dominance Determination**: Identifies non-dominant eye based on longer reaction times
6. **Results Display**: Shows average reaction times for left and right non-dominant positions
7. **Auto-Configuration**: When starting main task after practice, automatically sets optimal suppressor position
8. **Fallback Handling**: If no accurate responses are recorded, displays 0 for that eye's value

### Alpha Transition Control

The stimulus alpha transition has been enhanced for greater experimental control:

- **Fine-Grained Alpha Range**: Transitions between 0.00 (completely transparent) and 0.99 (nearly opaque)
- **Bidirectional Transitions**:
  - **Normal Mode (default)**: Stimulus fades IN from invisible (α=0.00) to visible (α=0.99)
  - **Reverse Mode**: Stimulus fades OUT from visible (α=0.99) to invisible (α=0.00)
- **Smooth Animation**: 50ms update intervals ensure fluid visual transitions
- **Independent Control**: Alpha transition is independent of mask refresh rate
- **Configurable Duration**: Set transition time from 3000ms to 100000ms
- **Computational Efficiency**: Transition granularity has minimal computational overhead

### Suppressor Switching

The suppressor switching functionality provides flexible control:

- **Practice Mode**: Automatic switching at predetermined trial points (5, 10, 15) based on sequence
- **Main Task Mode**: Optional manual configuration of single switching point
- **Real-Time Repositioning**: Seamless repositioning of visual elements without disrupting the experiment
- **Position Verification**: Console output confirms successful position switches

### Inter-Trial Interval (ITI) Customization

Complete control over inter-trial messaging:

- **Customizable Message Text**: Set any message text (default: "Press SPACE to continue")
- **Adjustable Delay**: Configure delay before message appears (default: 500ms)
- **Clean Display**: Messages appear only during ITI, not during stimulus presentation
- **Consistent Positioning**: Messages appear below fixation point in center of canvas

### Exit and Navigation Controls

Clear and intuitive control flow:

- **'q' Key**: Terminates current task and returns to configuration window
  - Saves all data collected up to that point
  - Does NOT exit the application
  - Allows starting a new task or adjusting settings
  
- **'Exit' Button (in Config UI)**: Cleanly exits the entire application
  - Presents confirmation dialog
  - Closes all windows and terminates process
  
- **'X' Button (Window Close)**: Exits the entire application
  - Saves any pending data
  - Closes all windows and terminates process
  
- **Task Completion**: Automatically returns to configuration window
  - Saves all trial data
  - Shows practice results if applicable
  - Ready to start new task

### Data Collection and Analysis

The experiment collects comprehensive data including:

- **Participant ID**: Unique identifier set in configuration (default: 1111)
- **Trial Number**: Sequential identifier for each trial within session
- **Y Position**: Vertical position of the stimulus in pixels
- **Stimulus Position**: Categorical position (top/bottom) based on Y coordinate
- **Image Path**: File path of the presented stimulus image
- **Reaction Time**: Time from stimulus onset to response in milliseconds
- **Response**: Key pressed by participant ('a' for top, 'z' for bottom, 'space' for skip)
- **Suppressor Position**: Side where the mask was presented (left/right)
- **Accuracy**: Correctness of response (1=correct, 0=incorrect)
- **From Practice**: Indicates if the trial was from practice mode (Yes/No)

## Installation and Setup

1. Clone the repository or download the source code

2. Set up a virtual environment and install dependencies:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

3. Run the experiment:
```bash
python display_file.py
```

## Usage Guide

### Configuration Window

When you start the application, a configuration window appears with the following options:

#### Basic Experiment Settings

- **Total Trials**: Number of trials in the experiment (recommended: 40-100 for main task)
  - Practice mode is fixed at 20 trials
  
- **Mask Directory**: Location of Mondrian mask images
  - Default: `mask_dir/`
  - Click "Browse" to select custom directory
  - Recommended image size: 640x800 pixels
  
- **Stimulus Directory**: Location of target stimulus images
  - Default: `stim_dir/`
  - Click "Browse" to select custom directory
  - Recommended image size: 200x300 pixels
  
- **Suppressor Position**: Left or right side presentation of masks
  - Use slider to select left (0) or right (1)
  - Automatically configured after practice mode

#### Timing and Visual Parameters

- **Stimulus Transition Duration**: Duration for alpha transition (3000-100000ms)
  - Default: 10000ms (10 seconds)
  - Controls how quickly stimulus fades in or out
  - **Reverse Checkbox**: Check to reverse alpha direction (visible→invisible)
  
- **Mask Refresh Rate**: Mask cycle time (17-10000ms)
  - Default: 100ms (10 Hz)
  - Recommended: 7-12 Hz for optimal suppression
  - Independent of stimulus alpha transitions
  
- **Canvas Background Color**: Background color of display canvas
  - Default: #808080 (medium grey)
  - Click color preview square to open color picker
  - Hex color format required

#### Inter-Trial Interval Settings

- **Interval Message Delay**: Delay before showing ITI message (ms)
  - Default: 500ms
  - Range: 0-10000ms
  - Controls pause before "continue" message appears
  
- **Interval Message Text**: Custom text displayed during ITI
  - Default: "Press SPACE to continue"
  - Can be any text string
  - Displayed in white Arial 16pt font

#### Advanced Options

- **Switch Suppressor**: Option to switch suppressor position mid-task
  - Check box to enable
  - Specify trial number for switch
  - Must be less than total trials
  - Note: Practice mode has automatic switching at trials 5, 10, 15

#### Participant Information

- **Participant ID**: Unique identifier included in all output data
  - Default: 1111
  - Included in CSV export for data management
  
#### Practice Results Display

After completing practice trials, results appear showing:
- **Left NonDom**: Average reaction time when suppressor is on right (left eye receiving stimulus)
- **Right NonDom**: Average reaction time when suppressor is on left (right eye receiving stimulus)
- Highlighted value indicates slower (more suppressed) eye
- Values of "---" or "0" indicate no accurate responses collected

### Control Buttons

- **Practice Trials**: Starts practice mode (20 trials, automatic switching)
- **Main Task (after practice)**: Starts main task with practice-determined configuration
  - Enabled only after completing practice
  - Uses optimal suppressor position based on dominance
- **Start with this configuration**: Starts main task with current settings
  - Available at any time
  - Does not require practice completion
- **Clear Data**: Resets all data files and configuration
  - Deletes practice_trial_data.csv, trial_data.csv, temp_main_config.json
  - Resets participant ID and practice results
  - Requires confirmation
- **Exit**: Cleanly closes the application
  - Requires confirmation
  - Saves no data (use 'q' during task to save and return)

### Experiment Flow

#### Option 1: With Practice Mode (Recommended for Eye Dominance Determination)

1. **Configure Settings**: Set up your experiment parameters in the configuration window
2. **Start Practice**: Click "Practice Trials" button
3. **Complete Practice**: 
   - Press SPACE to start each trial
   - Press 'a' for top stimulus, 'z' for bottom stimulus
   - Complete all 20 trials
   - Press 'q' to terminate early (returns to config with data saved)
4. **Review Results**: Practice results appear showing non-dominant eye measurements
5. **Start Main Task**: Click "Main Task (after practice)" to use optimal configuration
6. **Complete Main Task**: Run through your configured number of trials
7. **Retrieve Data**: Both practice and main task data saved to separate CSV files

#### Option 2: Direct Main Task (Without Practice)

1. **Configure Settings**: Set up your experiment parameters
2. **Set Suppressor Manually**: Choose left or right based on prior knowledge or preference
3. **Start Task**: Click "Start with this configuration"
4. **Complete Trials**: Run through your configured number of trials
5. **Retrieve Data**: Main task data saved to trial_data.csv

#### Option 3: Multiple Sessions

1. **Between Sessions**: 
   - Use "Clear Data" to reset files
   - Or manually rename/move CSV files to preserve previous data
2. **Change Participant**: Update Participant ID for each new subject
3. **Adjust Parameters**: Modify any settings as needed between sessions

### During Task Execution

#### Key Controls

- **SPACE**: 
  - Start a trial (when ITI message is showing)
  - Stop stimulus presentation (during trial)
  
- **'a' Key**: Respond that stimulus appeared in TOP position
  - Recorded as response
  - Accuracy calculated based on actual position
  
- **'z' Key**: Respond that stimulus appeared in BOTTOM position
  - Recorded as response
  - Accuracy calculated based on actual position
  
- **'q' Key**: Terminate current task
  - Saves all data collected so far
  - Returns to configuration window
  - Does NOT exit application
  - Allows starting new task or adjusting settings

#### Visual Display

- **Checkerboard Border**: High-contrast border around display area
- **Grey Canvas**: Central display area (color customizable)
- **Fixation Cross**: White '+' symbol at center (always visible)
- **Masks**: Mondrian patterns cycling on suppressor side
- **Stimulus**: Target image fading in or out on opposite side
- **ITI Message**: Custom message during inter-trial interval

### Data Retrieval

#### Practice Data (`practice_trial_data.csv`)

Contains all practice trial information:
- 20 trials total
- Both accurate and inaccurate responses
- Suppressor positions alternate (5L5R5L5R or 5R5L5R5L)
- "From Practice" column marked as "Yes"
- Used for dominance calculation

#### Main Task Data (`trial_data.csv`)

Contains main experiment data:
- Number of trials as configured
- Can include practice data if main task started after practice
- "From Practice" column distinguishes practice from main trials
- Includes participant ID for data management

#### CSV Format

Both files include the following columns:
```
Participant ID, Trial Number, Y Position, Stimulus Position, Image Path, 
Reaction Time, Response, Suppressor Position, Accuracy, From Practice
```

## Configuration Parameters Reference

### Complete List of Configurable Parameters

All parameters are saved to `config.json`:

```json
{
  "participant_id": "string (default: '1111')",
  "trials_total": "integer (default: 5, practice: 20)",
  "mask_dir": "string path (default: 'mask_dir')",
  "stim_dir": "string path (default: 'stim_dir')",
  "mask_position": "string 'left' or 'right' (default: 'left')",
  "blend_duration": "integer 3000-100000 ms (default: 10000)",
  "mask_cycle_time": "integer 17-10000 ms (default: 100)",
  "border_offset": "integer pixels (default: 0)",
  "iti_message_delay": "integer ms (default: 500)",
  "iti_message_text": "string (default: 'Press SPACE to continue')",
  "canvas_bg_color": "string hex color (default: '#808080')",
  "alpha_reverse": "boolean (default: false)",
  "switch_suppressor": "boolean (default: false)",
  "switch_trial": "integer trial number (default: 0)",
  "is_practice": "boolean (set by practice mode)",
  "practice_sequence": "array of 'left'/'right' (set by practice mode)"
}
```

## Best Practices and Tips

### Experiment Design

- **Eye Dominance**: Run practice mode first if eye dominance is unknown or relevant to your research
- **Mask Refresh Rate**: Keep between 7-12 Hz (85-143ms) for optimal suppression effect
- **Trial Count**: Use at least 40 trials for reliable measurements in main task
- **Alpha Transition**: 
  - Use normal mode (fade-in) for breakthrough CFS paradigms
  - Use reverse mode (fade-out) for suppression onset experiments
  - Typical duration: 5000-15000ms for gradual suppression breaking
- **Stimulus Size**: Keep stimuli 200x300 pixels for consistent presentation
- **Background Color**: Use medium grey (#808080) to balance luminance

### Data Management

- **Participant IDs**: Use consistent ID format across your study (e.g., P001, P002)
- **File Preservation**: Rename or move CSV files between sessions to prevent overwriting
  - Example: `trial_data.csv` → `trial_data_P001_session1.csv`
- **Backup**: Regularly backup your data files during long experiment sessions
- **Clear Between Subjects**: Use "Clear Data" button between participants

### Display Setup

- **Stereoscope Required**: Use mirror stereoscope or similar binocular viewing apparatus
- **Screen Position**: Position stereoscope mirrors to separate left/right visual fields
- **Viewing Distance**: Maintain consistent viewing distance (typically 50-70cm)
- **Screen Resolution**: Ensure adequate resolution for smooth alpha transitions
- **Refresh Rate**: Use monitor with ≥60Hz refresh rate

### Stimulus Preparation

- **Image Format**: PNG or JPG format supported
- **Recommended Size**: 
  - Stimuli: 200x300 pixels
  - Masks: 640x800 pixels
- **Color Mode**: RGBA mode supported for transparency
- **File Organization**: Keep stimuli and masks in separate directories
- **Naming**: Use consistent file naming for easier data analysis

### Troubleshooting

#### Visual Issues

- **Visual Tearing**: Increase mask cycle time (e.g., from 100ms to 150ms)
- **Choppy Alpha Transitions**: Check CPU usage, reduce number of mask images
- **Masks Not Cycling**: Verify mask_dir contains valid PNG/JPG images
- **Stimulus Not Appearing**: Check stim_dir path and image formats

#### Functional Issues

- **Suppressor Not Switching**: 
  - Practice mode: Check console output for switch confirmations
  - Main task: Verify "Switch suppressor" checkbox is enabled
  - Ensure switch_trial < trials_total
- **Practice Results Not Showing**: 
  - Complete all 20 practice trials
  - Ensure at least some accurate responses were recorded
- **Data Not Saving**: Check write permissions in experiment directory
- **Config Not Loading**: Delete config.json to reset to defaults

#### Application Issues

- **Won't Close**: Use 'q' key to return to config, then click "Exit"
- **Stuck in Practice Loop**: This should no longer occur with updated exit logic
- **Config Window Not Appearing**: Check for hidden windows or restart application

## Technical Details

### Alpha Blending Implementation

The stimulus alpha blending uses PIL's `Image.blend()` function:
- Blends between transparent RGBA image (α=0) and stimulus image (α=0.99)
- Update interval: 50ms (20 frames per second)
- Alpha step size: `50ms / blend_duration`
- Example: For 10000ms duration: 0.005 per update = 200 steps total
- Smoother than discrete 2-decimal increments due to continuous calculation

### Practice Mode Algorithm

1. **Sequence Generation**: Random choice of starting position (L or R)
2. **Trial Structure**: 4 blocks of 5 trials each
3. **Position Pattern**: LLLLL → RRRRR → LLLLL → RRRRR (or reversed)
4. **Switch Points**: After trials 5, 10, and 15
5. **Analysis Window**: Trials 2-5, 7-10, 12-15, 17-20 (skip first of each block)
6. **Dominance Calculation**: Average RT of accurate trials per suppressor position
7. **Result Interpretation**: Slower RT indicates stronger suppression = non-dominant eye

### File Structure and Data Flow

```
Application Start
    ↓
Configuration Window (config_file.py)
    ↓
User Selection → config.json
    ↓
Display File Main (display_file.py)
    ↓
Create Modules (mask_file.py, stim_file.py)
    ↓
Base Module (base_module.py) loads config
    ↓
Trial Loop with Key Handlers
    ↓
Data Collection → trial_data list
    ↓
Task Completion or 'q' Press
    ↓
write_trial_data_to_csv()
    ↓
Save to CSV with Participant ID
    ↓
Return to Config or Exit
```

## Version History

### Current Version (Updated October 2025)

**New Features:**
- Added inter-trial message text customization
- Added alpha transition reverse mode (fade-out option)
- Enhanced alpha transition granularity (0.00 to 0.99)
- Improved exit logic and navigation controls

**Behavior Changes:**
- 'q' key now always returns to config (never exits app)
- 'Exit' button and window close now exit application
- Main task can run independently without practice completion
- Practice data optional for main task execution

**UI Improvements:**
- Added ITI message text input field
- Added "Reverse?" checkbox for alpha transitions
- Reorganized configuration window layout
- Enhanced practice results display

### Previous Versions

See git history for previous implementation details.

## References

Amd, M. (2024). Breaking continuous flash suppression: A psychophysical paradigm for investigating visual awareness. *Journal of Vision*.

## License and Citation

[Include your license information here]

When using this software in research, please cite:
```
Amd, M. (2024). Breaking Continuous Flash Suppression Task. 
GitHub repository: https://github.com/micahamd/FlashSuppression
```

## Support and Contact

For questions, bug reports, or feature requests:
- Open an issue on GitHub
- Contact: [your contact information]

---

**Last Updated**: October 2025  
**Maintainer**: Micah Amd  
**Python Version**: 3.8+  
**Dependencies**: See requirements.txt

