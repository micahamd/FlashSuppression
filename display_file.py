import tkinter as tk
import csv
from functools import partial
from mask_file import ImageCycler
from stim_file import Stimulus
from config_file import ConfigWindow
from base_module import load_config

def draw_checkerboard(outline, canvas, square_size=20, border_width=60):
    outline.delete("checkerboard")
    
    # Get the module canvas position relative to the outline canvas
    canvas_x = canvas.winfo_x()
    canvas_y = canvas.winfo_y()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    # Calculate the border area with a small offset to align checkerboard
    config = load_config()
    user_offset = config.get('border_offset', 6)  # Get user-defined offset to align border with canvas objects (6 on home PC)
    offset = (square_size // 2) + user_offset  # Half square size plus user-defined offset
    start_x = canvas_x - border_width - offset
    start_y = canvas_y - border_width - offset
    end_x = canvas_x + canvas_width + border_width - offset
    end_y = canvas_y + canvas_height + border_width - offset
    
    # Draw checkerboard pattern in the border area
    for i in range(start_x, end_x, square_size * 2):
        for j in range(start_y, end_y, square_size * 2):
            # Only draw if in the border area (not in the canvas area)
            if (i < canvas_x or i >= canvas_x + canvas_width or 
                j < canvas_y or j >= canvas_y + canvas_height):
                outline.create_rectangle(i, j, i + square_size, j + square_size, 
                                      fill="white", tags="checkerboard")
                outline.create_rectangle(i + square_size, j + square_size, 
                                      i + square_size * 2, j + square_size * 2, 
                                      fill="white", tags="checkerboard")

def create_module(root, module_class, image_dir, canvas_side, cycle_time=None):
    outline = tk.Canvas(root, bg="black")
    outline.pack(side=canvas_side, fill="both", expand=True)
    if module_class == ImageCycler:
        module = module_class(root=outline, image_dir=image_dir, cycle_time=cycle_time)
    else:
        module = module_class(root=outline, image_dir=image_dir)
    module.canvas.pack(side="top", fill="none", expand=True, padx=60, pady=60)
    
    def update_checkerboard(event=None):
        outline.update_idletasks()  # Ensure canvas positions are updated
        root.after(100, lambda: draw_checkerboard(outline, module.canvas))  # Small delay for stability
    
    outline.bind("<Configure>", update_checkerboard)
    root.after(100, update_checkerboard)  # Initial draw after window setup
    return module

trial_data = []

def handle_space_press(event, modules, trial_count, trials_total, response, switch_trial=None, main_root=None, mask_side=None):
    if trial_count[0] >= trials_total:
        print("All trials completed.")
        write_trial_data_to_csv(trial_data)
        for module in modules:
            module.root.quit()
        return

    # Get the current mask module and its side
    mask_module = modules[0] if isinstance(modules[0], ImageCycler) else modules[1]
    current_mask_side = mask_module.root.pack_info()['side']
        
    # Check if we need to switch positions (if we've reached or passed the switch trial)
    if switch_trial and trial_count[0] >= switch_trial:
        print(f"Switching suppressor positions for remaining trials (starting at trial {trial_count[0]})")
        # Get the current positions of modules
        mask_module = modules[0] if isinstance(modules[0], ImageCycler) else modules[1]
        stim_module = modules[0] if isinstance(modules[0], Stimulus) else modules[1]
        
        # Get current pack info
        mask_info = mask_module.root.pack_info()
        stim_info = stim_module.root.pack_info()
        
        # Swap sides
        mask_module.root.pack_forget()
        stim_module.root.pack_forget()
        
        new_mask_side = tk.RIGHT if mask_info['side'] == 'left' else tk.LEFT
        mask_module.root.pack(side=new_mask_side, fill="both", expand=True)
        stim_module.root.pack(side=tk.LEFT if new_mask_side == tk.RIGHT else tk.RIGHT, 
                            fill="both", expand=True)
        
        # Force update
        main_root.update_idletasks()
        
        # Update checkerboard after switching sides
        mask_module.root.after(100, lambda: draw_checkerboard(mask_module.root, mask_module.canvas))
        stim_module.root.after(100, lambda: draw_checkerboard(stim_module.root, stim_module.canvas))

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
            
            # Set Stimulus Position based on Y Position
            if 'Y Position' in trial_data_point:
                trial_data_point['Stimulus Position'] = 'top' if trial_data_point['Y Position'] < 400 else 'below'
                
                # Calculate accuracy based on response and position
                is_correct = (
                    (response == 'a' and trial_data_point['Stimulus Position'] == 'top') or
                    (response == 'z' and trial_data_point['Stimulus Position'] == 'below')
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
        # Just handle the space press during inter-trial interval without recording data
        for module in modules:
            module.handle_space_press(event)

def write_trial_data_to_csv(trial_data):
    with open('trial_data.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'Trial Number', 
            'Y Position',
            'Stimulus Position',
            'Image Path', 
            'Reaction Time', 
            'Response', 
            'Suppressor Position',
            'Accuracy'
        ])
        writer.writeheader()
        for data in trial_data:
            writer.writerow(data)

def main():
    global trial_data
    trial_data = []  # Reset trial data at start of each run
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
    
    # Get switch trial number from config if enabled
    switch_trial = None
    if config.get('switch_suppressor', False):
        switch_trial = int(config.get('switch_trial', 0))

    for key in ('<space>', 'a', 'z'):
        main_root.bind(key, partial(handle_space_press, 
                                  modules=[mask_module, stim_module], 
                                  trial_count=trial_count, 
                                  trials_total=trials_total, 
                                  response=key,
                                  switch_trial=switch_trial,
                                  main_root=main_root,
                                  mask_side=mask_position))

    def on_close():
        write_trial_data_to_csv(trial_data)
        main_root.destroy()

    main_root.protocol("WM_DELETE_WINDOW", on_close)
    main_root.mainloop()

if __name__ == "__main__":
    main()
    if config.get('switch_suppressor', False):
        switch_trial = int(config.get('switch_trial', 0))

    for key in ('<space>', 'a', 'z'):
        main_root.bind(key, partial(handle_space_press, 
                                  modules=[mask_module, stim_module], 
                                  trial_count=trial_count, 
                                  trials_total=trials_total, 
                                  response=key,
                                  switch_trial=switch_trial,
                                  main_root=main_root,
                                  mask_side=mask_position))

    def on_close():
        write_trial_data_to_csv(trial_data)
        main_root.destroy()

    main_root.protocol("WM_DELETE_WINDOW", on_close)
    main_root.mainloop()

if __name__ == "__main__":
    main()
