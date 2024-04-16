import tkinter as tk
import json
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
    # Initialize the module with a specified part of the root window
    if module_class == ImageCycler:
        module = module_class(root=root, image_dir=image_dir, cycle_time=cycle_time)
    else:
        module = module_class(root=root, image_dir=image_dir)
    module.canvas.pack(side=canvas_side, fill="both", expand=True)
    return module


trial_data = [] # List to store trial data

def handle_space_press(event, modules, trial_count, trials_total):
    if trial_count[0] >= trials_total:
        print("All trials completed.") # Check if all trials are completed
        write_trial_data_to_json(trial_data)  # Write trial data to JSON file
        for module in modules:
            module.root.quit()  # Optionally close the program
        return

    # Toggle the state of each module based on current trial state
    if modules[0].image_cycle_running:  # Assuming both modules share the running state
        # End of a trial
        for module in modules:
            image_y_position, image_path, reaction_time = module.handle_space_press(event)
            if image_y_position is not None:
                print(f"Y position: {image_y_position}")
                print(f"Image path: {image_path}")
                print(f"Reaction Time: {reaction_time * 1000}")
                trial_data.append({
                    'Trial Number': trial_count[0],
                    'Y Position': image_y_position,
                    'Image Path': image_path,
                    'Reaction Time': reaction_time * 1000
                })                          
        print(f"Trial {trial_count[0]} completed.")
        trial_count[0] += 1
    else:
        # Start of a trial
        for module in modules:
            module.handle_space_press(event)

def write_trial_data_to_json(trial_data):
    with open('trial_data.json', 'w') as output_file:
        json.dump(trial_data, output_file)

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

    # Bind space press to a unified handler
    main_root.bind('<space>', lambda event: handle_space_press(event, [mask_module, stim_module], trial_count, trials_total))

    def on_close():
        """Handle the application close event."""
        write_trial_data_to_json(trial_data)
        main_root.destroy()

    main_root.protocol("WM_DELETE_WINDOW", on_close)  # Attach the close handler
    main_root.mainloop()

if __name__ == "__main__":
    main()
