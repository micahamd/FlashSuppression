import tkinter as tk
import tkinter.messagebox as messagebox
import csv
import json
import os
import sys
import subprocess
import time
from functools import partial
from mask_file import ImageCycler
from stim_file import Stimulus
from config_file import ConfigWindow
from base_module import load_config

def create_module(root, module_class, image_dir, canvas_side, cycle_time=None):
    # Create a frame to hold the module with padding for centering
    frame = tk.Frame(root, bg="black")
    # Pack with equal weight to ensure symmetric positioning
    frame.pack(side=canvas_side, fill="both", expand=True)

    # Configure the frame's grid weights to center content
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # Create the module with integrated border
    if module_class == ImageCycler:
        module = module_class(root=frame, image_dir=image_dir, cycle_time=cycle_time)
    else:
        module = module_class(root=frame, image_dir=image_dir)

    # Store the side information directly on the module for easier access
    module.side = canvas_side
    # Store the frame for easier access
    module.frame = frame
    # Store the module type for easier identification
    module.type = 'mask' if module_class == ImageCycler else 'stim'

    print(f"Created {module.type} module with side: {canvas_side}")

    return module

trial_data = []
iti_start_time = [None]  # Track when ITI message was shown
last_response_time = [0]  # Track last response time for debouncing
RESPONSE_DEBOUNCE_MS = 200  # Minimum time between responses in milliseconds (increased from 100)

def handle_key_press(event, modules, trial_count, trials_total, switch_trial=None, main_root=None):
    # Debounce: ignore responses that come too quickly
    current_time = time.time() * 1000  # Convert to milliseconds
    if current_time - last_response_time[0] < RESPONSE_DEBOUNCE_MS:
        print(f"Response ignored (debounce): {event.keysym}")
        return
    
    last_response_time[0] = current_time
    
    # Get the response key (space, a, z, or q)
    response = event.keysym
    # Convert 'space' to '<space>' for consistency
    if response == 'space':
        response = '<space>'

    # Check if 'q' was pressed to terminate the task and return to config
    if response == 'q':
        print("Task terminated by user. Returning to configuration window.")
        # Save any pending data
        for module in modules:
            if hasattr(module, 'save_trial_data'):
                module.save_trial_data()

        # Determine if practice mode
        config = load_config()
        is_practice = config.get('is_practice', False)
        
        # Save data appropriately
        write_trial_data_to_csv(trial_data, is_practice)
        
        # Close current window
        if main_root:
            main_root.destroy()
        
        # Always return to config (never exit app)
        subprocess.Popen([sys.executable, 'display_file.py', '--show-config'])
        return
    
    if trial_count[0] >= trials_total:
        print(f"Current phase completed ({trial_count[0]} trials).")
        # Check if we're in practice mode
        config = load_config()
        is_practice = config.get('is_practice', False)
        auto_progress = config.get('auto_progress_to_main', False)
        
        # Write trial data (append mode for continuous session)
        write_trial_data_to_csv(trial_data, is_practice, append_mode=False)

        # Check if we should auto-progress to main task
        if is_practice and auto_progress:
            print("Practice completed. Transitioning to main task...")
            
            # Calculate suppressor position from practice data
            calculated_position = calculate_dominance_from_practice_data(trial_data)
            
            if calculated_position:
                print(f"Calculated suppressor position: {calculated_position.upper()}")
            else:
                print("Warning: Could not calculate dominance. Using config default.")
                calculated_position = config.get('mask_position', 'left')
            
            # Update config for main task
            main_task_trials = config.get('main_task_trials', 20)
            config['is_practice'] = False
            config['auto_progress_to_main'] = False
            config['trials_total'] = main_task_trials
            config['mask_position'] = calculated_position
            config.pop('practice_sequence', None)  # Remove practice sequence
            
            # Save updated config
            with open('config.json', 'w') as file:
                json.dump(config, file)
            
            # STEP 1: Stop all module activity and reset state IMMEDIATELY
            print("=== STOPPING ALL MODULE ACTIVITY ===")
            for module in modules:
                # Cancel any pending ITI messages FIRST (critical!)
                if hasattr(module, 'cancel_iti_message'):
                    module.cancel_iti_message()
                    print(f"Cancelled pending ITI messages for {module.__class__.__name__}")
                
                # Stop any ongoing processes
                if hasattr(module, 'blending'):
                    module.blending = False
                if hasattr(module, 'image_cycle_running'):
                    module.image_cycle_running = False
                if hasattr(module, 'current_alpha'):
                    module.current_alpha = 0.0
                if hasattr(module, 'trial_start_time'):
                    module.trial_start_time = None
                if hasattr(module, 'first_space_press_time'):
                    module.first_space_press_time = None
                print(f"Stopped activity in {module.__class__.__name__}")
            
            # STEP 2: Clear ALL canvas content
            print("=== CLEARING ALL CANVASES ===")
            for module in modules:
                if hasattr(module, 'canvas'):
                    # Clear absolutely everything
                    module.canvas.delete('all')
                    print(f"Cleared canvas for {module.__class__.__name__}")
            
            # Force GUI update to apply clearing
            main_root.update_idletasks()
            main_root.update()

            # STEP 2.5: Switch stimulus directory if practice used a separate directory
            print("=== CHECKING STIMULUS DIRECTORY ===")
            practice_dir = config.get('practice_dir', None)
            main_stim_dir = config.get('stim_dir', 'stim_dir')

            # Get the stim module
            stim_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'stim'), None)

            if practice_dir and stim_module:
                # Practice used a separate directory, need to reload images from main stim_dir
                print(f"Switching stimulus directory from practice_dir to stim_dir: {main_stim_dir}")
                try:
                    # Update the image directory
                    stim_module.image_dir = main_stim_dir
                    # Reload images from the main stimulus directory
                    stim_module.images = stim_module.load_images()
                    # Reset the current image index
                    stim_module.current_image_index = 0
                    print(f"Successfully loaded {len(stim_module.images)} images from main stim_dir")
                except Exception as e:
                    print(f"Error loading images from main stim_dir: {e}")
            else:
                print("No directory switch needed - practice used same stim_dir as main task")

            # STEP 3: Reposition modules for main task
            print("=== REPOSITIONING MODULES ===")
            mask_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'mask'), None)
            if not stim_module:  # Get it again if we didn't get it above
                stim_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'stim'), None)
            
            if mask_module and stim_module:
                # Get the container
                container = mask_module.frame.master
                
                # Determine new positions
                initial_position = tk.LEFT if calculated_position == 'left' else tk.RIGHT
                opposite_position = tk.RIGHT if initial_position == tk.LEFT else tk.LEFT
                
                # Repack frames
                mask_module.frame.pack_forget()
                stim_module.frame.pack_forget()
                mask_module.frame.pack(side=initial_position, fill="both", expand=True)
                stim_module.frame.pack(side=opposite_position, fill="both", expand=True)
                
                # Update module attributes
                mask_module.side = initial_position
                stim_module.side = opposite_position
                
                container.update()
                print(f"Suppressor repositioned - Mask: {calculated_position}, Stim: {'right' if calculated_position == 'left' else 'left'}")
            
            # STEP 4: Redraw borders and fixation crosses
            print("=== REDRAWING VISUAL ELEMENTS ===")
            for module in modules:
                # Redraw checkerboard border if it exists
                if hasattr(module, 'draw_checkerboard_border'):
                    try:
                        module.draw_checkerboard_border(60)
                        print(f"Redrew border for {module.__class__.__name__}")
                    except Exception as e:
                        print(f"Could not redraw border: {e}")
                
                # Redraw content area if it exists
                if hasattr(module, 'content_area'):
                    try:
                        border_width = 60
                        module.content_area = module.canvas.create_rectangle(
                            border_width, border_width,
                            border_width + module.canvas_width, border_width + module.canvas_height,
                            fill=module.canvas_bg_color, outline='', tags='content_area'
                        )
                        print(f"Redrew content area for {module.__class__.__name__}")
                    except Exception as e:
                        print(f"Could not redraw content area: {e}")
                
                # Redraw fixation cross
                if hasattr(module, 'show_fixation'):
                    try:
                        module.show_fixation()
                        print(f"Redrew fixation for {module.__class__.__name__}")
                    except Exception as e:
                        print(f"Could not redraw fixation: {e}")
            
            # Force another GUI update
            main_root.update_idletasks()
            main_root.update()
            
            # STEP 5: Show standby window with longer delay
            print("=== SHOWING STANDBY WINDOW ===")
            iti_delay = config.get('iti_message_delay', 2000)
            # Use at least 2 seconds for transition
            transition_delay = max(iti_delay, 2000)
            show_standby_window(transition_delay)
            
            # STEP 6: Reset trial counter and data
            print("=== RESETTING TRIAL DATA ===")
            trial_count[0] = 0
            trial_data.clear()  # Clear practice data from memory (already saved to CSV)
            
            # Reset debounce timer to allow immediate responses in main task
            last_response_time[0] = 0
            
            # STEP 7: Rebind keys with updated trial counter and trials_total
            print("=== REBINDING KEYS ===")
            main_root.unbind_all('<space>')
            main_root.unbind_all('a')
            main_root.unbind_all('z')
            main_root.unbind_all('q')
            
            handler = partial(handle_key_press, modules=modules, trial_count=trial_count,
                            trials_total=main_task_trials, switch_trial=config.get('switch_trial'),
                            main_root=main_root)
            
            for key in ('<space>', 'a', 'z', 'q'):
                main_root.bind(key, handler)
            
            print("=== STARTING MAIN TASK ===")
            print(f"Main task: {main_task_trials} trials")
            
            # STEP 8: Additional delay and force GUI update
            main_root.update_idletasks()
            main_root.update()
            time.sleep(0.3)  # 300ms additional delay for stability

            # STEP 9: Show ITI message to prompt user to start first trial
            print("=== SHOWING ITI MESSAGE FOR FIRST TRIAL ===")
            # Schedule ITI message on both modules to ensure it appears
            for module in modules:
                if hasattr(module, 'schedule_iti_message'):
                    module.schedule_iti_message()
                    print(f"Scheduled ITI message for {module.__class__.__name__}")

            print("=== TRANSITION COMPLETE - Waiting for user to press SPACE ===")
            return
        else:
            # Not auto-progressing, close window and return to config
            if main_root:
                main_root.destroy()
            
            time.sleep(1)
            subprocess.Popen([sys.executable, 'display_file.py', '--show-config'])
            return

    # Get the current mask module and its side
    mask_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'mask'), None)
    if not mask_module:
        mask_module = modules[0] if isinstance(modules[0], ImageCycler) else modules[1]

    try:
        # Try to get the side from the module's side attribute first
        if hasattr(mask_module, 'side'):
            current_mask_side = 'left' if mask_module.side == tk.LEFT else 'right'
        else:
            # Fall back to getting it from the frame's pack info
            current_mask_side = 'left'  # Default to left if we can't determine
        print(f"Current mask side: {current_mask_side}")
    except Exception as e:
        # Default if we can't determine
        print(f"Error determining mask side: {e}, defaulting to 'left'")
        current_mask_side = 'left'

    # Check if we need to switch positions (if we've reached or passed the switch trial)
    if switch_trial and trial_count[0] >= switch_trial and not hasattr(main_root, 'switch_done'):
        print(f"Switching suppressor positions for remaining trials (starting at trial {trial_count[0]})")
        # Get the current positions of modules
        mask_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'mask'), None)
        stim_module = next((m for m in modules if hasattr(m, 'type') and m.type == 'stim'), None)

        if not mask_module or not stim_module:
            print("Could not identify mask and stim modules")
            return

        # Get the container (parent of the frames)
        container = mask_module.frame.master

        # Get current positions
        mask_frame = mask_module.frame
        stim_frame = stim_module.frame

        # Get current sides from the module attributes
        mask_side = mask_module.side
        stim_side = stim_module.side

        # Print current positions for debugging
        print(f"Current positions - Mask: {mask_side}, Stim: {stim_side}")

        # Unpack both frames
        mask_frame.pack_forget()
        stim_frame.pack_forget()

        # Swap sides
        new_mask_side = tk.RIGHT if mask_side == tk.LEFT else tk.LEFT
        new_stim_side = tk.LEFT if new_mask_side == tk.RIGHT else tk.RIGHT

        print(f"New positions - Mask: {'right' if new_mask_side == tk.RIGHT else 'left'}, Stim: {'right' if new_stim_side == tk.RIGHT else 'left'}")

        # Repack with swapped sides
        mask_frame.pack(side=new_mask_side, fill="both", expand=True)
        stim_frame.pack(side=new_stim_side, fill="both", expand=True)

        # Update the module's side attribute
        mask_module.side = new_mask_side
        stim_module.side = new_stim_side

        # Force update
        container.update()
        main_root.update()

        # Mark that we've done the switch so we don't do it again
        main_root.switch_done = True
        print("Switch completed successfully")

    # Find the stimulus and mask modules
    stim_module = next((module for module in modules if isinstance(module, Stimulus)), None)
    mask_module = next((module for module in modules if isinstance(module, ImageCycler)), None)

    # Check if we're in an inter-trial interval (both modules inactive)
    is_inter_trial = ((not stim_module.blending) and (not mask_module.image_cycle_running))

    # Only process trial data if we're not in an inter-trial interval
    if not is_inter_trial:
        trial_data_point = {}

        # Process module responses
        for module in modules:
            if hasattr(module, 'image_cycle_running') and module.image_cycle_running:
                image_y_position, image_path, reaction_time = module.handle_space_press(event)
                if image_y_position is not None:
                    trial_data_point['Y Position'] = image_y_position
                    trial_data_point['Image Path'] = image_path
                    trial_data_point['Reaction Time'] = reaction_time * 1000
            elif hasattr(module, 'blending') and module.blending:
                image_y_position, image_path, reaction_time = module.handle_space_press(event)
                if image_y_position is not None:
                    trial_data_point['Y Position'] = image_y_position
                    trial_data_point['Image Path'] = image_path
                    trial_data_point['Reaction Time'] = reaction_time * 1000
            else:
                module.handle_space_press(event)

        # Get the current Y position from the stimulus module if available
        if stim_module and stim_module.y_position and 'Y Position' not in trial_data_point:
            trial_data_point['Y Position'] = stim_module.y_position

        if trial_data_point:
            # Add trial metadata
            trial_data_point['Trial Number'] = trial_count[0]
            trial_data_point['Response'] = response
            trial_data_point['Suppressor Position'] = current_mask_side
            
            # Determine trial type based on config
            config = load_config()
            is_practice = config.get('is_practice', False)
            trial_data_point['Trial Type'] = 'Practice' if is_practice else 'Main'

            # Set Stimulus Position based on Y Position
            if 'Y Position' in trial_data_point:
                trial_data_point['Stimulus Position'] = 'top' if trial_data_point['Y Position'] < 400 else 'below'

                # Calculate accuracy based on response and position
                is_correct = (
                    (response == 'a' and trial_data_point['Stimulus Position'] == 'top') or
                    (response == 'z' and trial_data_point['Stimulus Position'] == 'below') or
                    (response == 'space' and True)  # Space is always considered correct for backward compatibility
                )
                trial_data_point['Accuracy'] = 1 if is_correct else 0
            else:
                # Default values if no position data
                trial_data_point['Stimulus Position'] = 'unknown'
                trial_data_point['Accuracy'] = 0
            trial_data.append(trial_data_point)
            print(f"Trial {trial_count[0]} completed.")
            trial_count[0] += 1
    else:
        # We're in an inter-trial interval - record ITI response
        # Calculate ITI reaction time
        iti_reaction_time = None
        if iti_start_time[0] is not None:
            iti_reaction_time = (time.time() - iti_start_time[0]) * 1000  # Convert to ms
        
        # Get ITI message text from config
        config = load_config()
        iti_message = config.get('iti_message_text', 'Press SPACE to continue')
        
        # Create ITI data point
        iti_data_point = {
            'Trial Number': trial_count[0],
            'Y Position': 'N/A',
            'Stimulus Position': 'N/A',
            'Image Path': iti_message,  # Store the ITI message shown
            'Reaction Time': iti_reaction_time if iti_reaction_time else 'N/A',
            'Response': response,
            'Suppressor Position': current_mask_side,
            'Accuracy': 'N/A',
            'Trial Type': 'ITI'
        }
        
        trial_data.append(iti_data_point)
        print(f"ITI response recorded: {response}, RT: {iti_reaction_time:.0f}ms" if iti_reaction_time else f"ITI response recorded: {response}")
        
        # Reset ITI start time for next interval
        iti_start_time[0] = None
        
        # Handle the space press in modules to advance to next trial
        for module in modules:
            module.handle_space_press(event)

def write_trial_data_to_csv(trial_data, is_practice=False, append_mode=False):
    """
    Write trial data to CSV file.
    
    Args:
        trial_data: List of trial data dictionaries
        is_practice: Legacy parameter, kept for compatibility but not used
        append_mode: If True, append to existing file; if False, create new file
    """
    # Always use single unified filename
    filename = 'trial_data.csv'

    # Get participant ID from config
    config = load_config()
    participant_id = config.get('participant_id', '1111')  # Default to 1111 if not found

    # Define fieldnames with Trial Type
    fieldnames = [
        'Participant ID',
        'Trial Number',
        'Trial Type',  # 'Practice', 'Main', or 'ITI'
        'Y Position',
        'Stimulus Position',
        'Image Path',
        'Reaction Time',
        'Response',
        'Suppressor Position',
        'Accuracy'
    ]

    # Determine write mode
    mode = 'a' if append_mode else 'w'
    write_header = not append_mode or not os.path.exists(filename)

    with open(filename, mode=mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header if needed
        if write_header:
            writer.writeheader()
        
        for data in trial_data:
            # Add participant ID to each row
            data_with_id = data.copy()
            data_with_id['Participant ID'] = participant_id
            writer.writerow(data_with_id)

def calculate_dominance_from_practice_data(trial_data):
    """
    Calculate non-dominant eye from practice trial data in memory.
    Returns the appropriate suppressor position for main task.
    
    Args:
        trial_data: List of trial data dictionaries from practice session
        
    Returns:
        'left' or 'right' for suppressor position, or None if calculation fails
    """
    try:
        left_rts = []
        right_rts = []
        
        # Filter for practice trials only (not ITI responses)
        practice_trials = [row for row in trial_data if row.get('Trial Type') == 'Practice']
        
        # Separate by suppressor position
        left_trials = [row for row in practice_trials if row['Suppressor Position'] == 'left']
        right_trials = [row for row in practice_trials if row['Suppressor Position'] == 'right']
        
        print(f"Found {len(left_trials)} left trials and {len(right_trials)} right trials")
        
        if len(left_trials) >= 2 and len(right_trials) >= 2:
            # Skip the first trial for each side and only include accurate responses
            left_rts = [float(row['Reaction Time']) for row in left_trials[1:]
                       if row.get('Reaction Time') not in ['N/A', None, '']
                       and row.get('Accuracy') == 1]
            right_rts = [float(row['Reaction Time']) for row in right_trials[1:]
                        if row.get('Reaction Time') not in ['N/A', None, '']
                        and row.get('Accuracy') == 1]
            
            print(f"Using {len(left_rts)} accurate left trials and {len(right_rts)} accurate right trials")
            print(f"Left RTs: {left_rts}")
            print(f"Right RTs: {right_rts}")
            
            # Calculate averages (only if there are accurate responses)
            left_avg = sum(left_rts) / len(left_rts) if left_rts else 0
            right_avg = sum(right_rts) / len(right_rts) if right_rts else 0
            
            print(f"Left avg: {left_avg:.0f}, Right avg: {right_avg:.0f}")
            
            # Higher reaction time = more suppression = non-dominant eye
            # We want to suppress the DOMINANT eye (opposite of non-dominant)
            # If left suppressor causes higher RT, left eye is non-dominant, so use RIGHT suppressor for main task
            # If right suppressor causes higher RT, right eye is non-dominant, so use LEFT suppressor for main task
            if left_avg > right_avg:
                return 'right'  # Left eye non-dom, suppress right (dominant) eye
            else:
                return 'left'   # Right eye non-dom, suppress left (dominant) eye
        else:
            print("Not enough trials to calculate dominance")
            return None
            
    except Exception as e:
        print(f"Error calculating dominance from practice data: {e}")
        return None

def calculate_dominance_from_practice():
    """Calculate non-dominant eye from practice data and return the appropriate suppressor position"""
    try:
        import csv
        left_rts = []
        right_rts = []

        with open('practice_trial_data.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

            # Get trials for each side
            left_trials = [row for row in rows if row['Suppressor Position'] == 'left']
            right_trials = [row for row in rows if row['Suppressor Position'] == 'right']

            print(f"Found {len(left_trials)} left trials and {len(right_trials)} right trials")

            if len(left_trials) >= 2 and len(right_trials) >= 2:
                # Skip the first trial for each side and only include accurate responses
                left_rts = [float(row['Reaction Time']) for row in left_trials[1:]
                           if 'Reaction Time' in row and row['Reaction Time']
                           and 'Accuracy' in row and row['Accuracy'] == '1']
                right_rts = [float(row['Reaction Time']) for row in right_trials[1:]
                            if 'Reaction Time' in row and row['Reaction Time']
                            and 'Accuracy' in row and row['Accuracy'] == '1']

                print(f"Using {len(left_rts)} accurate left trials and {len(right_rts)} accurate right trials")
                print(f"Left RTs: {left_rts}")
                print(f"Right RTs: {right_rts}")

                # Calculate averages (only if there are accurate responses)
                left_avg = sum(left_rts) / len(left_rts) if left_rts else 0
                right_avg = sum(right_rts) / len(right_rts) if right_rts else 0

                print(f"Left avg: {left_avg:.0f}, Right avg: {right_avg:.0f}")

                # Higher reaction time = more suppression = non-dominant eye
                # We want to suppress the DOMINANT eye (opposite of non-dominant)
                # If left suppressor causes higher RT, left eye is non-dominant, so use RIGHT suppressor for main task
                # If right suppressor causes higher RT, right eye is non-dominant, so use LEFT suppressor for main task
                if left_avg > right_avg:
                    return 'right'  # Left eye non-dom, suppress right (dominant) eye
                else:
                    return 'left'   # Right eye non-dom, suppress left (dominant) eye
            else:
                print("Not enough trials to calculate dominance")
                return None

    except Exception as e:
        print(f"Error calculating dominance from practice data: {e}")
        return None

def show_standby_window(iti_delay):
    """Show a brief 'standby' window before starting main task"""
    standby_root = tk.Tk()
    standby_root.title("Standby")
    
    # Center the window
    window_width = 300
    window_height = 150
    screen_width = standby_root.winfo_screenwidth()
    screen_height = standby_root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    standby_root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Add message
    message = tk.Label(standby_root, text="Preparing main task...\nPlease wait.",
                      font=("Arial", 14), pady=20)
    message.pack()
    
    # Disable window close button
    standby_root.protocol("WM_DELETE_WINDOW", lambda: None)
    
    # Show window
    standby_root.update()
    
    # Wait for ITI delay
    time.sleep(iti_delay / 1000.0)  # Convert ms to seconds
    
    # Close window
    standby_root.destroy()

def start_main_task_after_practice(main_task_config):
    """Start the main task using the saved configuration from practice"""
    try:
        # Calculate the suppressor position from practice data
        calculated_position = calculate_dominance_from_practice()
        
        if calculated_position:
            main_task_config['mask_position'] = calculated_position
            print(f"Setting mask position to {calculated_position.upper()} based on practice results")
        else:
            print("Warning: Could not calculate dominance. Using config default.")
        
        # Save the main task configuration
        with open('config.json', 'w') as file:
            json.dump(main_task_config, file)
        
        # Show standby window
        iti_delay = main_task_config.get('iti_message_delay', 2000)
        show_standby_window(iti_delay)
        
        # Start the main task
        print("Starting main task after practice...")
        subprocess.Popen([sys.executable, 'display_file.py'])
        
    except Exception as e:
        print(f"Error starting main task after practice: {e}")

def handle_practice_mode(config, mask_module, stim_module, trials_total):
    """Handle practice mode with alternating suppressor positions"""
    # Get the practice sequence from config
    practice_sequence = config.get('practice_sequence', [])
    if not practice_sequence or len(practice_sequence) != trials_total:
        print("Invalid practice sequence. Using default configuration.")
        # Create a default 5L5R5L5R sequence
        practice_sequence = ['left'] * 5 + ['right'] * 5 + ['left'] * 5 + ['right'] * 5
        if len(practice_sequence) > trials_total:
            practice_sequence = practice_sequence[:trials_total]

    # For 5L5R5L5R pattern, switch points are at trials 5, 10, and 15
    # These are the indices where we need to switch positions
    switch_points = [5, 10, 15]
    if len(practice_sequence) < 20:
        # Adjust switch points if we have fewer trials
        switch_points = [p for p in switch_points if p < len(practice_sequence)]

    print(f"Practice sequence: {practice_sequence[:5]}...{practice_sequence[-5:]}")
    print(f"Switch points: {switch_points}")

    # Set initial position based on the first item in the sequence
    initial_position = tk.LEFT if practice_sequence[0] == 'left' else tk.RIGHT
    opposite_position = tk.RIGHT if initial_position == tk.LEFT else tk.LEFT

    print(f"Setting initial mask position to {practice_sequence[0]}")

    # Get the frames
    mask_frame = mask_module.frame
    stim_frame = stim_module.frame

    # Get the container
    container = mask_frame.master

    # Set initial module positions
    mask_frame.pack_forget()
    stim_frame.pack_forget()

    # Pack with the correct sides
    mask_frame.pack(side=initial_position, fill="both", expand=True)
    stim_frame.pack(side=opposite_position, fill="both", expand=True)

    # Update the module's side attribute
    mask_module.side = initial_position
    stim_module.side = opposite_position

    print(f"Initial positions set - Mask: {'left' if initial_position == tk.LEFT else 'right'}, Stim: {'left' if opposite_position == tk.LEFT else 'right'}")

    # Force update to ensure positions are applied
    container.update()
    container.master.update()
    print("Initial position setup completed successfully")

    # Return the switch points for practice mode
    return switch_points

def show_config_window():
    """Show the configuration window and return the loaded config"""
    config_root = tk.Tk()
    config_window = ConfigWindow(config_root)
    config_root.mainloop()

    # Only proceed if a button was actually pressed (not just window closed)
    if not config_window.action_taken:
        print("Config window closed without action. Exiting.")
        sys.exit(0)

    return load_config()

def main():
    # Check if we're being called with special flags
    if len(sys.argv) > 1:
        # If we're called with --show-config, just show the config window
        if sys.argv[1] == '--show-config':
            show_config_window()
            return
        # If we're called with --start-main-task, skip the config window and start the main task directly
        elif sys.argv[1] == '--start-main-task':
            # We'll continue with the main function, but we'll set a flag to indicate
            # that we should use the existing config.json file
            print("Starting main task directly from practice results")
            # No need to return here, we'll continue with the main function

    global trial_data
    trial_data = []  # Reset trial data at start of each run
    from packaging_helper import get_resource_path

    # Use resource path resolution for directories
    default_mask_dir = get_resource_path('mask_dir')
    default_stim_dir = get_resource_path('stim_dir')

    # Check if we're starting the main task directly
    start_main_task_directly = len(sys.argv) > 1 and sys.argv[1] == '--start-main-task'

    if start_main_task_directly:
        # Load the config directly from the file
        config = load_config()
        # Set the after_practice flag
        config['after_practice'] = True
        print("Loaded configuration directly from file for main task")
    else:
        # Show configuration window and get config
        config = show_config_window()

    # Check if this is a main task after practice
    after_practice = config.get('after_practice', False)

    # If this is the main task after practice, load the practice data
    print(f"After practice flag: {after_practice}")
    if after_practice and os.path.exists('practice_trial_data.csv'):
        print("Loading practice data for main task...")
        try:
            import csv
            with open('practice_trial_data.csv', mode='r', newline='') as file:
                reader = csv.DictReader(file)
                practice_data = list(reader)

                # Convert string values to appropriate types
                for row in practice_data:
                    if 'Trial Number' in row:
                        row['Trial Number'] = int(row['Trial Number'])
                    if 'Reaction Time' in row and row['Reaction Time']:
                        row['Reaction Time'] = float(row['Reaction Time'])
                    if 'Accuracy' in row:
                        row['Accuracy'] = int(row['Accuracy'])
                    # Add a flag to indicate this is from practice
                    row['From Practice'] = 'Yes'

                # Add practice data to trial_data
                trial_data.extend(practice_data)
                print(f"Loaded {len(practice_data)} practice trials")
        except Exception as e:
            print(f"Error loading practice data: {e}")

    # Get configuration values with defaults to prevent KeyError
    try:
        trials_total = int(config.get('trials_total', 20))
    except (KeyError, ValueError, TypeError):
        # Default to 20 trials if there's any issue
        trials_total = 20
        print("Warning: Using default value of 20 for trials_total")

    try:
        cycle_time = int(config.get('mask_cycle_time', 100))
    except (ValueError, TypeError):
        # Default to 100ms if there's any issue
        cycle_time = 100
        print("Warning: Using default value of 100ms for mask_cycle_time")

    # Use the directories from config if provided, otherwise use defaults
    try:
        mask_dir = config.get('mask_dir', default_mask_dir) or default_mask_dir
    except (KeyError, TypeError):
        mask_dir = default_mask_dir
        print(f"Warning: Using default mask directory: {default_mask_dir}")

    try:
        stim_dir = config.get('stim_dir', default_stim_dir) or default_stim_dir
    except (KeyError, TypeError):
        stim_dir = default_stim_dir
        print(f"Warning: Using default stimulus directory: {default_stim_dir}")

    # Check if we're in practice mode and if a separate practice directory is specified
    is_practice = config.get('is_practice', False)
    practice_dir = config.get('practice_dir', None)

    # Determine which stimulus directory to use
    if is_practice and practice_dir:
        # Use practice directory for practice trials
        actual_stim_dir = practice_dir
        print(f"Using practice stimulus directory: {practice_dir}")
    else:
        # Use regular stim_dir (for main task or practice without separate dir)
        actual_stim_dir = stim_dir
        if is_practice:
            print(f"No separate practice directory specified - using stim_dir for practice: {stim_dir}")

    main_root = tk.Tk()
    main_root.title("Image Display Modules")
    main_root.geometry("1280x800")
    # Make the window maximized to ensure proper display
    main_root.state('zoomed')
    
    # Attach iti_start_time tracker to main_root so modules can access it
    main_root.iti_start_time = iti_start_time

    # Configure the main window to ensure symmetric layout
    main_root.grid_columnconfigure(0, weight=1)
    main_root.grid_columnconfigure(1, weight=1)
    main_root.grid_rowconfigure(0, weight=1)

    # Set up a container frame to ensure symmetric layout
    container = tk.Frame(main_root, bg="black")
    container.pack(fill="both", expand=True)

    # Configure the container for equal distribution
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=1)
    container.grid_rowconfigure(0, weight=1)

    # Make the window maximized to ensure proper display
    main_root.state('zoomed')

    # Note: is_practice was already determined above when setting actual_stim_dir

    # Set initial mask position with error handling
    try:
        mask_position = tk.LEFT if config.get('mask_position', 'left') == 'left' else tk.RIGHT
    except (KeyError, TypeError):
        # Default to left if there's any issue
        mask_position = tk.LEFT
        print("Warning: Using default left position for mask")

    stim_position = tk.RIGHT if mask_position == tk.LEFT else tk.LEFT

    mask_module = create_module(container, ImageCycler, mask_dir, mask_position, cycle_time)
    stim_module = create_module(container, Stimulus, actual_stim_dir, stim_position)

    trial_count = [0]

    # Handle switch trial logic
    if is_practice:
        # For practice mode, we'll use the practice sequence
        switch_points = handle_practice_mode(config, mask_module, stim_module, trials_total)
        print(f"Practice mode enabled with {trials_total} trials and switch points at {switch_points}")

        # Create a custom handler for practice mode that checks for switch points
        def practice_handler(event):
            # Get the response key
            response = event.keysym

            # Check if 'q' was pressed to terminate the practice
            if response == 'q':
                print("Practice terminated by user. Returning to configuration window.")
                # Save any pending data
                if hasattr(stim_module, 'save_trial_data'):
                    stim_module.save_trial_data()

                # Save practice data
                write_trial_data_to_csv(trial_data, is_practice=True)
                
                # Close current window
                main_root.destroy()
                
                # Return to config window
                subprocess.Popen([sys.executable, 'display_file.py', '--show-config'])
                return

            # Check if we're in an inter-trial interval (both modules inactive)
            is_inter_trial = ((not stim_module.blending) and (not mask_module.image_cycle_running))

            # Only process switching if it's a space press during inter-trial interval
            if response == 'space' and is_inter_trial:
                # Check if the NEXT trial count is in switch points
                # This ensures we switch BEFORE starting the next trial
                if switch_points and (trial_count[0] + 1) in switch_points:
                    print(f"Switching sides at trial {trial_count[0] + 1} (from {switch_points})")
                    # Get the target position directly from the practice sequence
                    sequence_index = trial_count[0] + 1

                    # Get the target position directly from the practice sequence
                    practice_sequence = config.get('practice_sequence', [])
                    if practice_sequence and sequence_index < len(practice_sequence):
                        target_position = practice_sequence[sequence_index]
                    else:
                        # Fallback to the 5L5R5L5R pattern if no sequence is available
                        if sequence_index < 5:
                            target_position = 'left'
                        elif sequence_index < 10:
                            target_position = 'right'
                        elif sequence_index < 15:
                            target_position = 'left'
                        else:
                            target_position = 'right'

                    print(f"Switching to {target_position} at trial {sequence_index}")

                    # Get the container (parent of the frames)
                    container = mask_module.frame.master

                    # Get current positions
                    mask_frame = mask_module.frame
                    stim_frame = stim_module.frame

                    # Get current sides from the module attributes
                    mask_side = mask_module.side
                    stim_side = stim_module.side

                    # Print current positions for debugging
                    print(f"Current positions - Mask: {mask_side}, Stim: {stim_side}")
                    print(f"Target position for mask: {target_position}")

                    # Unpack both frames
                    mask_frame.pack_forget()
                    stim_frame.pack_forget()

                    # Set positions based on target position
                    if target_position == 'left':
                        new_mask_side = tk.LEFT
                        new_stim_side = tk.RIGHT
                        print("Setting mask to LEFT, stim to RIGHT")
                    else:  # right
                        new_mask_side = tk.RIGHT
                        new_stim_side = tk.LEFT
                        print("Setting mask to RIGHT, stim to LEFT")

                    # Repack with new sides
                    mask_frame.pack(side=new_mask_side, fill="both", expand=True)
                    stim_frame.pack(side=new_stim_side, fill="both", expand=True)

                    # Update the module's side attribute
                    mask_module.side = new_mask_side
                    stim_module.side = new_stim_side

                    # Force update
                    container.update()
                    main_root.update()
                    print("Practice switch completed successfully")

            # Call the regular key press handler
            return handle_key_press(event, [mask_module, stim_module], trial_count, trials_total,
                                  None, main_root)

        # Bind the practice handler to space, a, z, and q keys
        for key in ('<space>', 'a', 'z', 'q'):
            main_root.bind(key, practice_handler)
    else:
        # Regular mode - use the switch_trial from config if enabled
        switch_trial = None
        if config.get('switch_suppressor', False):
            switch_trial = int(config.get('switch_trial', 0))
            print(f"Switch suppressor enabled, will switch after trial {switch_trial}")
            # Reset the switch_done flag to ensure it can switch
            if hasattr(main_root, 'switch_done'):
                delattr(main_root, 'switch_done')
                print("Reset switch_done flag")

        for key in ('<space>', 'a', 'z', 'q'):
            main_root.bind(key, partial(handle_key_press,
                                      modules=[mask_module, stim_module],
                                      trial_count=trial_count,
                                      trials_total=trials_total,
                                      switch_trial=switch_trial,
                                      main_root=main_root))

    def on_close():
        config = load_config()
        is_practice = config.get('is_practice', False)
        
        # Save any pending data
        write_trial_data_to_csv(trial_data, is_practice)
        
        # Close window
        main_root.destroy()
        
        # Exit application completely (no restart)
        sys.exit(0)

    main_root.protocol("WM_DELETE_WINDOW", on_close)
    main_root.mainloop()

if __name__ == "__main__":
    main()
