import tkinter as tk
from tkinter import filedialog, Scale, messagebox
import json

class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Configuration Settings")
        
        # Labels and entries for setting trials total
        self.trials_label = tk.Label(master, text="Enter Total Trials:")
        self.trials_label.grid(row=0, column=0)
        self.trials_entry = tk.Entry(master)
        self.trials_entry.grid(row=0, column=1)
        self.trials_entry.insert(0, "5")  # Default value

        # Labels and buttons for selecting directories
        self.mask_dir_label = tk.Label(master, text="Select Mask Directory:")
        self.mask_dir_label.grid(row=1, column=0)
        self.mask_dir_button = tk.Button(master, text="Browse", command=lambda: self.select_directory('mask'))
        self.mask_dir_button.grid(row=1, column=1)

        self.stim_dir_label = tk.Label(master, text="Select Stimulus Directory:")
        self.stim_dir_label.grid(row=2, column=0)
        self.stim_dir_button = tk.Button(master, text="Browse", command=lambda: self.select_directory('stim'))
        self.stim_dir_button.grid(row=2, column=1)

        # Slider for selecting module side
        self.side_label = tk.Label(master, text="Mask Module Position:")
        self.side_label.grid(row=3, column=0)
        self.side_scale = Scale(master, from_=0, to=1, orient=tk.HORIZONTAL, label="Left/Right", showvalue=0)
        self.side_scale.grid(row=3, column=1)
        self.side_scale.set(0)  # Default to left (0 for left, 1 for right)

        # Entry for blend duration
        self.duration_label = tk.Label(master, text="Set Blend Duration (1000 to 100000 ms):")
        self.duration_label.grid(row=4, column=0)
        self.duration_entry = tk.Entry(master)
        self.duration_entry.grid(row=4, column=1)
        self.duration_entry.insert(0, "10000")  # Default blend duration

        # Save button
        self.save_button = tk.Button(master, text="Save Configuration", command=self.save_config)
        self.save_button.grid(row=5, columnspan=2)

        # Directory storage
        self.directories = {
            'mask': "C:/Users/Admin/Python Projects/face_presentation/mond_masks",
            'stim': "C:/Users/Admin/Python Projects/face_presentation/face_folder"
        }

    def select_directory(self, module_type):
        directory = filedialog.askdirectory()
        if directory:
            self.directories[module_type] = directory

    def save_config(self):
        # Validate blend duration
        try:
            duration = int(self.duration_entry.get())
            if not 1000 <= duration <= 100000:
                raise ValueError("Duration out of allowed range")
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Blend Duration must be between 1000 and 100000 milliseconds")
            return

        config = {
            'trials_total': self.trials_entry.get(),
            'mask_dir': self.directories['mask'],
            'stim_dir': self.directories['stim'],
            'mask_position': "left" if self.side_scale.get() == 0 else "right",
            'blend_duration': duration
        }
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file)
        self.master.destroy()

def main():
    root = tk.Tk()
    app = ConfigWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
