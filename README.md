# A (breaking) Continuous Flash Suppression task

This b-CFS task, described in Amd (2024), presents a target stimulus to one eye and dynamic Mondrian masks to the alternate eye. 

## Configuration Options

- **Trials Total**: Number of trials in the experiment
- **Mask Directory**: Location of mask images (default: mask_dir/)
- **Stimulus Directory**: Location of stimulus images (default: stim_dir/)
- **Suppressor Position**: Left or right side presentation of masks
- **Blend Duration**: Duration for the stimulus to become fully opaque from a fully transparent state (3000-100000ms)
- **Mask Cycle Time**: Mask cycle rate (17-10000ms).
- **Border Offset**: Alignment adjustment (adjust this in case the checkerboard border and canvas objects don't align on your display)
- **ITI Message Delay**: Delay before showing continue message during inter-trial interval
- **Switch Suppressor**: Option to switch suppressor position during the trial sequence. Useful for practice runs and assessing sighting dominance.

## File Structure

- `display_file.py`: Application entry point and display coordination
- `config_file.py`: Configuration GUI for task
- `base_module.py`: Base class settings across stimulus and mask presentations
- `stim_file.py`: Stimulus presentation module
- `mask_file.py`: Mask presentation module
- `config.json`: Configuration setting for task
- `mask_dir/`: Directory containing mask images
- `stim_dir/`: Directory containing stimulus images

## Usage

1. Run the experiment in a virtual environment:
```bash
python -m venv venv
python venv\Scripts\activate
pip install -r requirements.txt
python display_file.py
```

2. Configure settings in the GUI:
   - Total number of trials
   - Mask and stimulus directories
   - Suppressor position (left/right)
   - Stimulus transition duration (3000-100000ms)
   - Mask refresh rate (17-10000ms)
   - Border-Canvas offset
   - Inter-trial interval message delay
   - Optional suppressor position switching

3. During the experiment:
   - Press SPACE to start each trial
   - Press 'a' for top position responses
   - Press 'z' for bottom position responses
   - Trial data is automatically saved

## Data Collection

The experiment automatically saves trial data including:
- Trial number
- Stimulus position
- Response
- Reaction time
- Accuracy
- Suppressor position

Data is saved to 'trial_data.csv' in the project directory.

## Notes

- The canvas dimensions have been hard-coded to replicate Amd's (2024) design. These can be altered to accomodate your setup.
- Mask refresh rates under 7 Hz are not recommended due to tearing artefacts, but this could be a threading issue.
- Ensure to rename the trial data file after each run, otherwise this will be overridden after the subsequentg run. 
- The 'stim_dir' and 'mask_dir' directories can be altered in the configuration. This can be useful for practice trials.
- The 'Swith Suppressor' option will alternate the position of the suppressor after the marked trial, and will persist for remaining trials. Use this during a practice run (10 trials each side) to identify the non-dominant eye. Then, the main run can focus on a single side. 
