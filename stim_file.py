import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import os
from base_module import BaseModule, load_config

class Stimulus(BaseModule):
    def __init__(self, image_dir, root=None):
        config = load_config()
        self.duration = int(config.get('blend_duration', 10000))
        self.alpha_reverse = config.get('alpha_reverse', False)
        super().__init__(root=root if root else tk.Tk(), image_dir=image_dir, resize_dims=(200, 300))
        self.root.configure(bg='black')
        self.current_image_index = 0
        self.blending = False
        self.alpha = 0
        self.update_interval = 50
        self.y_position = 0
        self.root.after(100, self.place_fixation_point)
        # Bind all key press events
        for key in ('<space>', 'a', 'z'):
            self.root.bind(key, self.handle_space_press)
        self.first_space_press_time = None
        self.image_y_position = None
        self.image_path = None

    def blend_image(self):
        if not self.blending:
            return
        
        # Calculate alpha increment/decrement
        alpha_step = self.update_interval / self.duration
        
        if self.alpha_reverse:
            # Reverse: decrease from 0.99 to 0
            self.alpha -= alpha_step
            if self.alpha < 0:
                self.alpha = 0
        else:
            # Normal: increase from 0 to 0.99
            self.alpha += alpha_step
            if self.alpha > 0.99:
                self.alpha = 0.99
        
        transparent_img = Image.new("RGBA", self.pil_images[self.current_image_index].size, self.RGB_CONSTANT)
        blended = Image.blend(transparent_img, self.pil_images[self.current_image_index], self.alpha)
        tk_img = ImageTk.PhotoImage(blended)

        # Determine the center position based on whether we have a border
        if hasattr(self, 'content_area'):
            border_width = 60
            center_x = border_width + (self.canvas_width / 2)
            # Adjust y_position for border
            adjusted_y_position = border_width + self.y_position
        else:
            center_x = self.canvas_width / 2
            adjusted_y_position = self.y_position

        self.canvas.create_image(center_x, adjusted_y_position, anchor=tk.N, image=tk_img, tags="stim_image")
        self.canvas.image = tk_img
        self.image_y_position = self.y_position  # Store the original y_position (without border adjustment)
        self.image_path = self.image_files[self.current_image_index]
        
        # Check stopping condition based on direction
        if self.alpha_reverse:
            should_continue = self.alpha > 0
        else:
            should_continue = self.alpha < 0.99
        
        if should_continue:
            self.root.after(self.update_interval, self.blend_image)
        else:
            self.blending = False

    def start_blend(self):
        self.first_space_press_time = time.time()
        self.blending = True
        
        # Set initial alpha based on direction
        if self.alpha_reverse:
            self.alpha = 0.99  # Start at maximum visibility
        else:
            self.alpha = 0     # Start invisible
        
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.y_position = random.choice([50, 450])
        self.blend_image()

    def handle_space_press(self, event):
        if self.blending:
            self.blending = False

            # AGGRESSIVE: Clear stimulus image, ITI messages, and any stray text
            self.canvas.delete("stim_image")
            self.canvas.delete("iti_message")
            self.canvas.delete("text")  # Catch any untagged text
            
            # Also clear by searching for all text items
            all_items = self.canvas.find_all()
            for item in all_items:
                if self.canvas.type(item) == 'text':
                    # Only delete if it's not the fixation cross (which should be recreated anyway)
                    self.canvas.delete(item)

            # If we have a border, redraw the content area
            if hasattr(self, 'content_area'):
                border_width = 60
                self.content_area = self.canvas.create_rectangle(
                    border_width, border_width,
                    border_width + self.canvas_width, border_width + self.canvas_height,
                    fill=self.canvas_bg_color, outline='', tags='content_area'
                )

            self.place_fixation_point()
            if self.first_space_press_time:
                reaction_time = time.time() - self.first_space_press_time
            else:
                reaction_time = None
            self.first_space_press_time = None
            # Show ITI message after configured delay
            self.schedule_iti_message()
            return self.image_y_position, self.image_path, reaction_time
        else:
            # AGGRESSIVE: Clear any existing ITI message and text before starting new trial
            self.canvas.delete("iti_message")
            self.canvas.delete("text")
            
            # Also clear by searching for all text items except fixation
            all_items = self.canvas.find_all()
            for item in all_items:
                if self.canvas.type(item) == 'text':
                    self.canvas.delete(item)
            
            # Redraw fixation before starting
            if hasattr(self, 'place_fixation_point'):
                self.place_fixation_point()
            
            self.start_blend()
            return None, None, None

    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     stimulus = Stimulus('C:/Users/Admin/Python Projects/face_presentation/face_folder')
#     stimulus.run()
