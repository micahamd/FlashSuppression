import tkinter as tk
import csv
import json
from functools import partial
from mask_file import ImageCycler
from stim_file import Stimulus
from config_file import ConfigWindow

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {
            'trials_total': 5,  # Default number of trials if no config file is found
            'mask_dir': "C:/Users/Admin/Python Projects/face_presentation/mond_masks",
            'stim_dir': "C:/Users/Admin/Python Projects/face_presentation/face_folder",
            'mask_position': 'left'  # Default position of mask module
        }

def create_module(root, module_class, image_dir, canvas_side, cycle_time=None):
    # Create a frame with a black background to act as the outline
    frame = tk.Frame(root, background="black")
    frame.pack(side=canvas_side, fill="both", expand=True)

    # Initialize the module with a specified part of the root window
    if module_class == ImageCycler:
        module = module_class(root=frame, image_dir=image_dir, cycle_time=cycle_time)
    else:
        module = module_class(root=frame, image_dir=image_dir)

    # Pack the canvas with a margin to create the outline effect
    module.canvas.pack(side="top", fill="none", expand=False, pady=50)  # Add padding here

    return module

trial_data = [] # List to store trial data

def handle_space_press(event, modules, trial_count, trials_total, response):
    if trial_count[0] >= trials_total:
        print("All trials completed.")
        write_trial_data_to_csv(trial_data)
        for module in modules:
            module.root.quit()
        return

    if modules[0].image_cycle_running:
        for module in modules:
            image_y_position, image_path, reaction_time = module.handle_space_press(event)
            if image_y_position is not None:
                trial_data.append({
                    'Trial Number': trial_count[0],
                    'Y Position': image_y_position,
                    'Image Path': image_path,
                    'Reaction Time': reaction_time * 1000,
                    'Response': response  # Now correctly records the key used
                })
        print(f"Trial {trial_count[0]} completed.")
        trial_count[0] += 1
    else:
        for module in modules:
            module.handle_space_press(event)

def write_trial_data_to_csv(trial_data):
    with open('trial_data.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Trial Number', 'Y Position', 'Image Path', 'Reaction Time', 'Response'])
        writer.writeheader()
        for data in trial_data:
            writer.writerow(data)

def main():
    # Start with the configuration window
    config_root = tk.Tk()
    config_app = ConfigWindow(config_root)
    config_root.mainloop()

    # Load the configuration
    config = load_config()
    trials_total = int(config['trials_total'])
    cycle_time = int(config.get('mask_cycle_time', 100))  # Load cycle time from config or default to 100 ms

    # Start the main application
    main_root = tk.Tk()
    main_root.title("Image Display Modules")
    main_root.geometry("1280x800")

    # Determine module positions based on config
    mask_position = tk.LEFT if config['mask_position'] == 'left' else tk.RIGHT
    stim_position = tk.RIGHT if mask_position == tk.LEFT else tk.LEFT

    # Create both modules side by side, passing cycle_time to ImageCycler
    mask_module = create_module(main_root, ImageCycler, config['mask_dir'], mask_position, cycle_time)
    stim_module = create_module(main_root, Stimulus, config['stim_dir'], stim_position)

    # Trial count tracker
    trial_count = [0]

    # Bind each key using a loop with functools.partial to handle the response key
    for key in ('<space>', 'a', 'z'):
        main_root.bind(key, partial(handle_space_press, modules=[mask_module, stim_module], trial_count=trial_count, trials_total=trials_total, response=key))

    def on_close():
        write_trial_data_to_csv(trial_data)
        main_root.destroy()

    main_root.protocol("WM_DELETE_WINDOW", on_close)  # Attach the close handler
    main_root.mainloop()

if __name__ == "__main__":
    main()
