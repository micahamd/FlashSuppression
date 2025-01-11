import tkinter as tk
from tkinter import filedialog, Scale, messagebox
import json

class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("b-CFS Configuration Settings")
        self.master.geometry("500x300")  # Set window size

        # Use padding and consistent grid placement for a cleaner look
        self.master['padx'] = 10
        self.master['pady'] = 10

        # Directory storage
        self.directories = {
            'mask': "mask_dir",
            'stim': "stim_dir"
        }

        # Trials total
        self.trials_label = tk.Label(master, text="Enter Total Trials:")
        self.trials_label.grid(row=0, column=0, sticky='w')
        self.trials_entry = tk.Entry(master)
        self.trials_entry.grid(row=0, column=1, sticky='w')
        self.trials_entry.insert(0, "5")  # Default value

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

        # Mask module position
        self.side_label = tk.Label(master, text="Suppressor Position:")
        self.side_label.grid(row=3, column=0, sticky='w')
        self.side_scale = Scale(master, from_=0, to=1, orient=tk.HORIZONTAL, label="Left/Right", showvalue=0)
        self.side_scale.grid(row=3, column=1, sticky='w')
        self.side_scale.set(0)  # Default to left (0 for left, 1 for right)

        # Stimulus transition duration
        self.duration_label = tk.Label(master, text="Stimulus transition duration (3000 to 100000 ms):")
        self.duration_label.grid(row=4, column=0, sticky='w')
        self.duration_entry = tk.Entry(master)
        self.duration_entry.grid(row=4, column=1, sticky='w')
        self.duration_entry.insert(0, "10000")  # Default blend duration 10s

        # Mask cycle time
        self.cycle_time_label = tk.Label(master, text="Mask refresh (17 to 10000 ms):")
        self.cycle_time_label.grid(row=5, column=0, sticky='w')
        self.cycle_time_entry = tk.Entry(master)
        self.cycle_time_entry.grid(row=5, column=1, sticky='w')
        self.cycle_time_entry.insert(0, "100")  # Default cycle time

        # Border-Canvas offset
        self.offset_label = tk.Label(master, text="Border-Canvas offset (for alignment):")
        self.offset_label.grid(row=6, column=0, sticky='w')
        self.offset_entry = tk.Entry(master)
        self.offset_entry.grid(row=6, column=1, sticky='w')
        self.offset_entry.insert(0, "6")  # Default offset value

        # Switch suppressor checkbox and trial entry
        self.switch_var = tk.BooleanVar(value=False)
        self.switch_label = tk.Label(master, text="Switch suppressor?")
        self.switch_label.grid(row=7, column=0, sticky='w')
        self.switch_checkbox = tk.Checkbutton(master, variable=self.switch_var, command=self.toggle_switch_entry)
        self.switch_checkbox.grid(row=7, column=1, sticky='w')

        self.switch_trial_label = tk.Label(master, text="After how many trials?")
        self.switch_trial_label.grid(row=8, column=0, sticky='w')
        self.switch_trial_entry = tk.Entry(master, state='disabled')
        self.switch_trial_entry.grid(row=8, column=1, sticky='w')
        self.switch_trial_entry.insert(0, "0")

        # Save button
        self.save_button = tk.Button(master, text="Start with this configuration", command=self.save_config)
        self.save_button.grid(row=9, column=0, columnspan=2, pady=10)  # Add some padding around the save button

    def select_directory(self, module_type):
        directory = filedialog.askdirectory()
        if directory:
            self.directories[module_type] = directory

    def toggle_switch_entry(self):
        """Enable/disable the switch trial entry based on checkbox state"""
        if self.switch_var.get():
            self.switch_trial_entry.config(state='normal')
        else:
            self.switch_trial_entry.config(state='disabled')
            self.switch_trial_entry.delete(0, tk.END)
            self.switch_trial_entry.insert(0, "0")

    def save_config(self):
        # Validate blend duration and mask cycle time
        try:
            duration = int(self.duration_entry.get())
            cycle_time = int(self.cycle_time_entry.get())
            trials_total = int(self.trials_entry.get())
            
            if not 3000 <= duration <= 100000 or not 17 <= cycle_time <= 10000:
                raise ValueError("Input out of allowed range")

            # Validate switch trial count if checkbox is checked
            if self.switch_var.get():
                switch_trial = int(self.switch_trial_entry.get())
                if switch_trial >= trials_total:
                    messagebox.showerror("Invalid Input", "Switch trial count must be less than total trials")
                    return
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Stimulus Blend Duration must be between 3000 and 100000 milliseconds. Mask Cycle Time must be between 17 and 10000 milliseconds.")
            return

        # Save configuration to file
        config = {
            'trials_total': trials_total,
            'mask_dir': self.directories['mask'],
            'stim_dir': self.directories['stim'],
            'mask_position': "left" if self.side_scale.get() == 0 else "right",
            'blend_duration': duration,
            'mask_cycle_time': cycle_time,
            'border_offset': int(self.offset_entry.get()),
            'switch_suppressor': self.switch_var.get(),
            'switch_trial': int(self.switch_trial_entry.get()) if self.switch_var.get() else 0
        }

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        self.master.destroy()
