import tkinter as tk
from tkinter import filedialog, Scale, messagebox
import json

class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Configuration Settings")
        self.master.geometry("500x300")  # Set window size

        # Use padding and consistent grid placement for a cleaner look
        self.master['padx'] = 10
        self.master['pady'] = 10

        # Directory storage
        self.directories = {
            'mask': "C:/Users/Admin/Python Projects/face_presentation/mond_masks",
            'stim': "C:/Users/Admin/Python Projects/face_presentation/face_folder"
        }

        # Trials total
        self.trials_label = tk.Label(master, text="Enter Total Trials:")
        self.trials_label.grid(row=0, column=0, sticky='w')
        self.trials_entry = tk.Entry(master)
        self.trials_entry.grid(row=0, column=1, sticky='w')
        self.trials_entry.insert(0, "5")  # Default value

        # Mask directory
        self.mask_dir_label = tk.Label(master, text="Select Mask Directory:")
        self.mask_dir_label.grid(row=1, column=0, sticky='w')
        self.mask_dir_button = tk.Button(master, text="Browse", command=lambda: self.select_directory('mask'))
        self.mask_dir_button.grid(row=1, column=1, sticky='w')

        # Stimulus directory
        self.stim_dir_label = tk.Label(master, text="Select Stimulus Directory:")
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
        self.duration_label = tk.Label(master, text="Stimulus transition (3000 to 100000 ms):")
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

        # Save button
        self.save_button = tk.Button(master, text="Save Configuration", command=self.save_config)
        self.save_button.grid(row=6, column=0, columnspan=2, pady=10)  # Add some padding around the save button

    def select_directory(self, module_type):
        directory = filedialog.askdirectory()
        if directory:
            self.directories[module_type] = directory

    def save_config(self):
        # Validate blend duration and mask cycle time
        try:
            duration = int(self.duration_entry.get())
            cycle_time = int(self.cycle_time_entry.get())
            if not 3000 <= duration <= 100000 or not 17 <= cycle_time <= 10000:
                raise ValueError("Input out of allowed range")
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Stimulus Blend Duration must be between 3000 and 100000 milliseconds. Mask Cycle Time must be between 17 and 10000 milliseconds.")
            return

        # Save configuration to file
        config = {
            'trials_total': self.trials_entry.get(),
            'mask_dir': self.directories['mask'],
            'stim_dir': self.directories['stim'],
            'mask_position': "left" if self.side_scale.get() == 0 else "right",
            'blend_duration': duration,
            'mask_cycle_time': cycle_time  # Add mask cycle time to the config
        }

        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        self.master.destroy()