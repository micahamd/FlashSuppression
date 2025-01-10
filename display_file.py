import tkinter as tk
import csv
from functools import partial
from mask_file import ImageCycler
from stim_file import Stimulus
from config_file import ConfigWindow
from base_module import load_config

def draw_checkerboard(canvas, square_size=20):
    canvas.delete("checkerboard")
    for i in range(0, canvas.winfo_width(), square_size * 2):
        for j in range(0, canvas.winfo_height(), square_size * 2):
            canvas.create_rectangle(i, j, i + square_size, j + square_size, fill="grey", tags="checkerboard")
            canvas.create_rectangle(i + square_size, j + square_size, i + square_size * 2, j + square_size * 2, fill="black", tags="checkerboard")

def create_module(root, module_class, image_dir, canvas_side, cycle_time=None):
    outline = tk.Canvas(root, bg="black")
    outline.pack(side=canvas_side, fill="both", expand=True)
    outline.bind("<Configure>", lambda event: draw_checkerboard(outline))
    if module_class == ImageCycler:
        module = module_class(root=outline, image_dir=image_dir, cycle_time=cycle_time)
    else:
        module = module_class(root=outline, image_dir=image_dir)
    module.canvas.pack(side="top", fill="none", expand=True, padx=20, pady=20)
    return module

trial_data = []

def handle_space_press(event, modules, trial_count, trials_total, response):
    if trial_count[0] >= trials_total:
        print("All trials completed.")
        write_trial_data_to_csv(trial_data)
        for module in modules:
            module.root.quit()
        return

    trial_data_point = {}
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

    if trial_data_point:
        trial_data_point['Trial Number'] = trial_count[0]
        trial_data_point['Response'] = response
        trial_data.append(trial_data_point)
        print(f"Trial {trial_count[0]} completed.")
        trial_count[0] += 1

def write_trial_data_to_csv(trial_data):
    with open('trial_data.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Trial Number', 'Y Position', 'Image Path', 'Reaction Time', 'Response'])
        writer.writeheader()
        for data in trial_data:
            writer.writerow(data)

def main():
    # Hard-coded directory paths with correct folder names
    default_mask_dir = 'C:/Users/micah/Downloads/Python Proj/cfs-task/FlashSuppression/mask_dir'
    default_stim_dir = 'C:/Users/micah/Downloads/Python Proj/cfs-task/FlashSuppression/stim_dir'

    config_root = tk.Tk()
    config_app = ConfigWindow(config_root)
    config_root.mainloop()

    config = load_config()
    trials_total = int(config['trials_total'])
    cycle_time = int(config.get('mask_cycle_time', 100))

    # Use the directories from config if provided, otherwise use defaults
    mask_dir = config['mask_dir'] if 'mask_dir' in config and config['mask_dir'] else default_mask_dir
    stim_dir = config['stim_dir'] if 'stim_dir' in config and config['stim_dir'] else default_stim_dir

    main_root = tk.Tk()
    main_root.title("Image Display Modules")
    main_root.geometry("1280x800")

    mask_position = tk.LEFT if config['mask_position'] == 'left' else tk.RIGHT
    stim_position = tk.RIGHT if mask_position == tk.LEFT else tk.LEFT

    mask_module = create_module(main_root, ImageCycler, mask_dir, mask_position, cycle_time)
    stim_module = create_module(main_root, Stimulus, stim_dir, stim_position)

    trial_count = [0]

    for key in ('<space>', 'a', 'z'):
        main_root.bind(key, partial(handle_space_press, modules=[mask_module, stim_module], trial_count=trial_count, trials_total=trials_total, response=key))

    def on_close():
        write_trial_data_to_csv(trial_data)
        main_root.destroy()

    main_root.protocol("WM_DELETE_WINDOW", on_close)
    main_root.mainloop()

if __name__ == "__main__":
    main()
