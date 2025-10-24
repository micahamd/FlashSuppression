import tkinter as tk
from tkinter import filedialog, Scale, messagebox
import json
import os
import random
import sys
import subprocess
from base_module import load_config

class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("b-CFS Configuration Settings")
        self.master.geometry("600x550")  # Increased window size for practice directory option

        # Use padding and consistent grid placement for a cleaner look
        self.master['padx'] = 10
        self.master['pady'] = 10
        
        # Flag to track if window was closed vs a button was pressed
        self.action_taken = False

        # Directory storage
        self.directories = {
            'mask': "mask_dir",
            'stim': "stim_dir",
            'practice': None  # Optional - if None, will use stim_dir for practice
        }
        
        # Load persistent settings
        persistent_settings = self.load_persistent_settings()

        # Trials total
        self.trials_label = tk.Label(master, text="Enter Total Trials:")
        self.trials_label.grid(row=0, column=0, sticky='w')
        self.trials_entry = tk.Entry(master)
        self.trials_entry.grid(row=0, column=1, sticky='w')
        self.trials_entry.insert(0, persistent_settings.get('trials_total', '5'))  # Load saved or default

        # Mask directory
        self.mask_dir_label = tk.Label(master, text="Select Mask Directory (default: mask_dir/):")
        self.mask_dir_label.grid(row=1, column=0, sticky='w')
        self.mask_dir_button = tk.Button(master, text="Browse", command=lambda: self.select_directory('mask'))
        self.mask_dir_button.grid(row=1, column=1, sticky='w')

        # Stimulus directory
        self.stim_dir_label = tk.Label(master, text="Select Stimulus Directory (default: stim_dir/):")
        self.stim_dir_label.grid(row=2, column=0, sticky='w')
        self.stim_dir_button = tk.Button(master, text="Browse", command=lambda: self.select_directory('stim'))
        self.stim_dir_button.grid(row=2, column=1, sticky='w')

        # Practice directory (optional)
        self.practice_dir_label = tk.Label(master, text="Practice Stimulus Directory (optional):")
        self.practice_dir_label.grid(row=3, column=0, sticky='w')

        # Create frame for practice directory button and status
        self.practice_dir_frame = tk.Frame(master)
        self.practice_dir_frame.grid(row=3, column=1, sticky='w')

        self.practice_dir_button = tk.Button(self.practice_dir_frame, text="Browse",
                                             command=lambda: self.select_directory('practice'))
        self.practice_dir_button.pack(side=tk.LEFT)

        # Status label to show if practice dir is set
        self.practice_dir_status = tk.Label(self.practice_dir_frame, text="(using stim_dir)",
                                           fg="gray", font=("Arial", 8))
        self.practice_dir_status.pack(side=tk.LEFT, padx=5)

        # Clear button for practice directory
        self.practice_dir_clear_button = tk.Button(self.practice_dir_frame, text="Clear",
                                                   command=self.clear_practice_directory,
                                                   state='disabled')
        self.practice_dir_clear_button.pack(side=tk.LEFT, padx=2)

        # Mask module position
        self.side_label = tk.Label(master, text="Suppressor Position:")
        self.side_label.grid(row=4, column=0, sticky='w')
        self.side_scale = Scale(master, from_=0, to=1, orient=tk.HORIZONTAL, label="Left/Right", showvalue=0)
        self.side_scale.grid(row=4, column=1, sticky='w')
        self.side_scale.set(persistent_settings.get('mask_position_value', 0))  # Load saved or default to left

        # Stimulus transition duration
        self.duration_label = tk.Label(master, text="Stimulus transition duration (3000 to 100000 ms):")
        self.duration_label.grid(row=5, column=0, sticky='w')

        # Create frame for duration entry and reverse checkbox
        self.duration_frame = tk.Frame(master)
        self.duration_frame.grid(row=5, column=1, sticky='w')

        self.duration_entry = tk.Entry(self.duration_frame, width=10)
        self.duration_entry.pack(side=tk.LEFT)
        self.duration_entry.insert(0, persistent_settings.get('blend_duration', '10000'))  # Load saved or default

        # Add reverse checkbox
        self.reverse_alpha_var = tk.BooleanVar(value=persistent_settings.get('reverse_alpha', False))
        self.reverse_alpha_checkbox = tk.Checkbutton(self.duration_frame, text="Reverse?",
                                                     variable=self.reverse_alpha_var)
        self.reverse_alpha_checkbox.pack(side=tk.LEFT, padx=10)

        # Mask cycle time
        self.cycle_time_label = tk.Label(master, text="Mask refresh (17 to 10000 ms):")
        self.cycle_time_label.grid(row=6, column=0, sticky='w')
        self.cycle_time_entry = tk.Entry(master)
        self.cycle_time_entry.grid(row=6, column=1, sticky='w')
        self.cycle_time_entry.insert(0, persistent_settings.get('mask_cycle_time', '100'))  # Load saved or default

        # Canvas Background Color
        self.bg_color_label = tk.Label(master, text="Canvas Background Color:")
        self.bg_color_label.grid(row=7, column=0, sticky='w')

        # Create a frame to hold the color entry and color preview
        self.color_frame = tk.Frame(master)
        self.color_frame.grid(row=7, column=1, sticky='w')

        # Load color from config if it exists, otherwise use standard grey (#808080)
        config = load_config()
        default_color = config.get('canvas_bg_color', '#808080')

        # Make sure it's a valid hex color
        if not default_color.startswith('#') or len(default_color) != 7:
            default_color = '#808080'  # Default to grey if invalid

        self.bg_color_var = tk.StringVar(value=default_color)
        self.bg_color_entry = tk.Entry(self.color_frame, textvariable=self.bg_color_var, width=8)
        self.bg_color_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Color preview button that opens color chooser when clicked
        self.color_preview = tk.Button(self.color_frame, width=3, height=1, bg=default_color,
                                    command=self.choose_color)
        self.color_preview.pack(side=tk.LEFT)

        # Create a hidden entry to maintain compatibility with border offset
        self.offset_entry = tk.Entry(master)
        self.offset_entry.insert(0, "0")

        # Interval message delay
        self.delay_label = tk.Label(master, text="Interval message delay (ms):")
        self.delay_label.grid(row=8, column=0, sticky='w')
        self.delay_entry = tk.Entry(master)
        self.delay_entry.grid(row=8, column=1, sticky='w')
        self.delay_entry.insert(0, persistent_settings.get('iti_message_delay', '500'))  # Load saved or default

        # ITI message text customization
        self.iti_text_label = tk.Label(master, text="Interval message text:")
        self.iti_text_label.grid(row=9, column=0, sticky='w')
        self.iti_text_entry = tk.Entry(master, width=30)
        self.iti_text_entry.grid(row=9, column=1, sticky='w')
        self.iti_text_entry.insert(0, persistent_settings.get('iti_message_text', 'Press SPACE to continue'))  # Load saved or default

        # Switch suppressor checkbox and trial entry
        self.switch_var = tk.BooleanVar(value=persistent_settings.get('switch_suppressor', False))
        self.switch_label = tk.Label(master, text="Switch suppressor?")
        self.switch_label.grid(row=10, column=0, sticky='w')
        self.switch_checkbox = tk.Checkbutton(master, variable=self.switch_var, command=self.toggle_switch_entry)
        self.switch_checkbox.grid(row=10, column=1, sticky='w')

        self.switch_trial_label = tk.Label(master, text="After how many trials?")
        self.switch_trial_label.grid(row=11, column=0, sticky='w')
        switch_state = 'normal' if persistent_settings.get('switch_suppressor', False) else 'disabled'
        self.switch_trial_entry = tk.Entry(master, state=switch_state)
        self.switch_trial_entry.grid(row=11, column=1, sticky='w')
        self.switch_trial_entry.insert(0, persistent_settings.get('switch_trial', '0'))

        # Participant ID field
        self.id_label = tk.Label(master, text="Participant ID:")
        self.id_label.grid(row=12, column=0, sticky='w')

        # Create a frame to hold the ID entry
        self.id_frame = tk.Frame(master)
        self.id_frame.grid(row=12, column=1, sticky='w')

        # Load saved participant ID or default to 1111
        self.participant_id = tk.StringVar(value=persistent_settings.get('participant_id', '1111'))
        self.id_entry = tk.Entry(self.id_frame, textvariable=self.participant_id, width=10)
        self.id_entry.pack(side=tk.LEFT)

        # Buttons frame for better layout
        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=13, column=0, columnspan=2, pady=10)

        # Practice checkbox - load saved state
        self.practice_var = tk.BooleanVar(value=persistent_settings.get('practice_enabled', False))
        self.practice_checkbox = tk.Checkbutton(self.button_frame, text="Practice?",
                                                variable=self.practice_var,
                                                command=self.toggle_practice_mode)
        self.practice_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Apply initial practice mode state
        if self.practice_var.get():
            self.toggle_practice_mode()

        # Start task button (renamed from "Main Task")
        self.main_task_button = tk.Button(self.button_frame, text="Start Task",
                                          command=self.start_main_task)
        self.main_task_button.pack(side=tk.LEFT, padx=5)

        # Clear button to reset configuration and discard data
        self.clear_button = tk.Button(self.button_frame, text="Clear Data",
                                   command=self.clear_data, bg="#ccccff")
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Exit button to cleanly close the application
        self.exit_button = tk.Button(self.button_frame, text="Exit",
                                  command=self.exit_application, bg="#ffcccc")
        self.exit_button.pack(side=tk.LEFT, padx=5)
        
        # Set up window close protocol to handle 'X' button
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_window_close(self):
        """Handle window close ('X' button) - exit application completely"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            self.master.destroy()
            sys.exit(0)

    def toggle_practice_mode(self):
        """Enable/disable suppressor position based on practice checkbox"""
        if self.practice_var.get():
            # Practice enabled - disable suppressor position
            self.side_scale.config(state='disabled')
            # Create tooltip binding
            self.side_scale.bind('<Enter>', self.show_practice_tooltip)
            self.side_scale.bind('<Leave>', self.hide_practice_tooltip)
        else:
            # Practice disabled - enable suppressor position
            self.side_scale.config(state='normal')
            # Remove tooltip binding
            self.side_scale.unbind('<Enter>')
            self.side_scale.unbind('<Leave>')
            if hasattr(self, 'tooltip_window'):
                self.tooltip_window.destroy()

    def show_practice_tooltip(self, event):
        """Show tooltip explaining why suppressor is disabled"""
        self.tooltip_window = tk.Toplevel(self.master)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        label = tk.Label(self.tooltip_window, 
                        text="Suppressor position will be determined\nby practice trial results",
                        background="lightyellow", relief="solid", borderwidth=1, padx=5, pady=5)
        label.pack()

    def hide_practice_tooltip(self, event):
        """Hide tooltip"""
        if hasattr(self, 'tooltip_window'):
            self.tooltip_window.destroy()

    def select_directory(self, module_type):
        directory = filedialog.askdirectory()
        if directory:
            self.directories[module_type] = directory

            # Update practice directory status if practice dir was selected
            if module_type == 'practice':
                self.practice_dir_status.config(text=f"({os.path.basename(directory)})", fg="green")
                self.practice_dir_clear_button.config(state='normal')
                print(f"Practice directory set to: {directory}")

    def clear_practice_directory(self):
        """Clear the practice directory selection"""
        self.directories['practice'] = None
        self.practice_dir_status.config(text="(using stim_dir)", fg="gray")
        self.practice_dir_clear_button.config(state='disabled')
        print("Practice directory cleared - will use stim_dir for practice trials")

    def choose_color(self):
        """Open a color chooser dialog and update the color preview and entry"""
        from tkinter import colorchooser
        # Get the current color from the entry
        current_color = self.bg_color_var.get()
        # Make sure it's a valid hex color
        if not current_color.startswith('#') or len(current_color) != 7:
            current_color = '#808080'  # Default to grey if invalid

        # Open the color chooser dialog
        color = colorchooser.askcolor(color=current_color, title="Choose Canvas Background Color")

        # If a color was selected (not cancelled)
        if color and color[1]:
            # Update the entry with the hex value
            self.bg_color_var.set(color[1])
            # Update the preview button color
            self.color_preview.config(bg=color[1])

    def toggle_switch_entry(self):
        """Enable/disable the switch trial entry based on checkbox state"""
        if self.switch_var.get():
            self.switch_trial_entry.config(state='normal')
        else:
            self.switch_trial_entry.config(state='disabled')
            self.switch_trial_entry.delete(0, tk.END)
            self.switch_trial_entry.insert(0, "0")

    def validate_inputs(self):
        """Validate user inputs and return a tuple of (is_valid, duration, cycle_time, trials_total)"""
        try:
            duration = int(self.duration_entry.get())
            cycle_time = int(self.cycle_time_entry.get())
            trials_total = int(self.trials_entry.get())

            if not 3000 <= duration <= 100000 or not 17 <= cycle_time <= 10000:
                messagebox.showerror("Invalid Input", "Stimulus Blend Duration must be between 3000 and 100000 milliseconds. Mask Cycle Time must be between 17 and 10000 milliseconds.")
                return False, None, None, None

            # Validate switch trial count if checkbox is checked
            if self.switch_var.get():
                switch_trial = int(self.switch_trial_entry.get())
                if switch_trial >= trials_total:
                    messagebox.showerror("Invalid Input", "Switch trial count must be less than total trials")
                    return False, None, None, None

            return True, duration, cycle_time, trials_total
        except ValueError:
            messagebox.showerror("Invalid Input", "Stimulus Blend Duration must be between 3000 and 100000 milliseconds. Mask Cycle Time must be between 17 and 10000 milliseconds.")
            return False, None, None, None

    def create_config_dict(self, trials_total, duration, cycle_time, is_practice=False, practice_sequence=None):
        """Create a configuration dictionary based on the current settings"""
        config = {
            'participant_id': self.participant_id.get(),
            'trials_total': trials_total,
            'mask_dir': self.directories['mask'],
            'stim_dir': self.directories['stim'],
            'practice_dir': self.directories['practice'],  # Can be None
            'mask_position': "left" if self.side_scale.get() == 0 else "right",
            'blend_duration': duration,
            'mask_cycle_time': cycle_time,
            'border_offset': int(self.offset_entry.get()),
            'iti_message_delay': int(self.delay_entry.get()),
            'iti_message_text': self.iti_text_entry.get(),
            'canvas_bg_color': self.bg_color_var.get(),
            'alpha_reverse': self.reverse_alpha_var.get(),
            'run_practice_first': self.practice_var.get()
        }

        # Add practice mode settings if applicable
        if is_practice:
            config['is_practice'] = True
            config['practice_sequence'] = practice_sequence
        else:
            # Add regular switch suppressor settings
            config['switch_suppressor'] = self.switch_var.get()
            config['switch_trial'] = int(self.switch_trial_entry.get()) if self.switch_var.get() else 0

        return config

    def start_main_task(self):
        """Start the main task (with optional practice first)"""
        # Validate inputs first
        is_valid, duration, cycle_time, trials_total = self.validate_inputs()
        if not is_valid:
            return

        # Mark that an action was taken
        self.action_taken = True
        
        # Check if we should run practice first
        run_practice = self.practice_var.get()
        
        if run_practice:
            # Generate practice configuration
            practice_trials = 20
            start_left = random.choice([True, False])
            
            if start_left:
                practice_sequence = ['left'] * 5 + ['right'] * 5 + ['left'] * 5 + ['right'] * 5
                print("Practice sequence: 5L, 5R, 5L, 5R")
            else:
                practice_sequence = ['right'] * 5 + ['left'] * 5 + ['right'] * 5 + ['left'] * 5
                print("Practice sequence: 5R, 5L, 5R, 5L")
            
            print(f"Full practice sequence: {practice_sequence}")
            print(f"Switch points should be at trials: 5, 10, 15")
            
            # Create practice config
            practice_config = self.create_config_dict(
                trials_total=practice_trials,
                duration=duration,
                cycle_time=cycle_time,
                is_practice=True,
                practice_sequence=practice_sequence
            )
            # Add flags to indicate main task follows
            practice_config['auto_progress_to_main'] = True
            practice_config['main_task_trials'] = trials_total
            
            # Save practice config
            with open('config.json', 'w') as config_file:
                json.dump(practice_config, config_file)
        else:
            # Just run main task
            config = self.create_config_dict(
                trials_total=trials_total,
                duration=duration,
                cycle_time=cycle_time
            )
            config['auto_progress_to_main'] = False
            
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file)
        
        # Save persistent settings before closing
        self.save_persistent_settings()
        
        # Close window and start task
        self.master.destroy()

    def clear_data(self):
        """Clear all data files and reset configuration"""
        # Show a confirmation dialog
        if messagebox.askyesno("Clear Data", "This will delete all data files. Continue?"):
            # List of files to remove
            files_to_remove = [
                'trial_data.csv',  # Single unified data file
                'temp_main_config.json',
                'config.json',
                # Note: config_ui_settings.json is NOT cleared to preserve UI preferences
            ]

            # Remove each file if it exists
            for file in files_to_remove:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        print(f"Removed {file}")
                    except Exception as e:
                        print(f"Error removing {file}: {e}")

            # Reset the participant ID to default
            self.participant_id.set("1111")

            # Show confirmation
            messagebox.showinfo("Clear Data", "All data files have been cleared.")

    def exit_application(self):
        """Cleanly exit the application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
            # Close the window
            self.master.destroy()
            # Exit the application completely
            sys.exit(0)

    def save_config(self):
        """Save the regular configuration and start the experiment"""
        # Validate inputs first
        is_valid, duration, cycle_time, trials_total = self.validate_inputs()
        if not is_valid:
            return

        # Mark that an action was taken
        self.action_taken = True

        # Create and save the configuration
        config = self.create_config_dict(
            trials_total=trials_total,
            duration=duration,
            cycle_time=cycle_time
        )

        # Make sure switch suppressor settings are included
        config['switch_suppressor'] = self.switch_var.get()
        if self.switch_var.get():
            config['switch_trial'] = int(self.switch_trial_entry.get())
            print(f"Switch suppressor enabled, will switch after trial {config['switch_trial']}")
        else:
            config['switch_trial'] = 0
            print("Switch suppressor disabled")

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        # Save persistent settings before closing
        self.save_persistent_settings()
        
        self.master.destroy()

    def load_persistent_settings(self):
        """Load persistent UI settings from file"""
        settings_file = 'config_ui_settings.json'
        default_settings = {
            'trials_total': '5',
            'mask_position_value': 0,
            'blend_duration': '10000',
            'reverse_alpha': False,
            'mask_cycle_time': '100',
            'iti_message_delay': '500',
            'iti_message_text': 'Press SPACE to continue',
            'switch_suppressor': False,
            'switch_trial': '0',
            'participant_id': '1111',
            'practice_enabled': False
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new fields
                    default_settings.update(loaded_settings)
                    print("Loaded persistent UI settings")
            except Exception as e:
                print(f"Error loading persistent settings: {e}")
        
        return default_settings
    
    def save_persistent_settings(self):
        """Save current UI settings to file for next session"""
        settings_file = 'config_ui_settings.json'
        
        try:
            settings = {
                'trials_total': self.trials_entry.get(),
                'mask_position_value': self.side_scale.get(),
                'blend_duration': self.duration_entry.get(),
                'reverse_alpha': self.reverse_alpha_var.get(),
                'mask_cycle_time': self.cycle_time_entry.get(),
                'iti_message_delay': self.delay_entry.get(),
                'iti_message_text': self.iti_text_entry.get(),
                'switch_suppressor': self.switch_var.get(),
                'switch_trial': self.switch_trial_entry.get(),
                'participant_id': self.participant_id.get(),
                'practice_enabled': self.practice_var.get()
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            print("Saved persistent UI settings")
        except Exception as e:
            print(f"Error saving persistent settings: {e}")
