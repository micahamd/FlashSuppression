import tkinter as tk
from PIL import Image, ImageTk
import os
import time
from base_module import BaseModule

class ImageCycler(BaseModule):
    def __init__(self, root, image_dir, cycle_time):
        super().__init__(root=root, image_dir=image_dir, canvas_width=640, canvas_height=800, resize_dims=(640, 800))
        self.cycle_time = cycle_time
        self.current_image_index = 0
        self.image_cycle_running = False
        # Bind all key press events
        for key in ('<space>', 'a', 'z'):
            self.root.bind(key, self.handle_space_press)

    def update_canvas(self):
        if not self.image_cycle_running:
            return
        # Clear the canvas except for the checkerboard border and content area
        self.canvas.delete("image", "iti_message")

        # Determine the center position based on whether we have a border
        if hasattr(self, 'content_area'):
            border_width = 60
            center_x = border_width + (self.canvas_width / 2)
            center_y = border_width + (self.canvas_height / 2)
        else:
            center_x = 320
            center_y = 400

        new_image = self.canvas.create_image(center_x, center_y, image=self.images[self.current_image_index], anchor='center', tags="image")
        self.canvas.itemconfig(new_image, tags="image")
        self.place_fixation_point()  # Ensure the fixation point is visible
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.root.after(self.cycle_time, self.update_canvas)

    def handle_space_press(self, event):
        if self.image_cycle_running:
            self.image_cycle_running = False

            # AGGRESSIVE: Clear image, ITI messages, and any stray text
            self.canvas.delete("image")
            self.canvas.delete("iti_message")
            self.canvas.delete("text")
            
            # Also clear by searching for all text items
            all_items = self.canvas.find_all()
            for item in all_items:
                if self.canvas.type(item) == 'text':
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
            # Show ITI message after configured delay
            self.schedule_iti_message()
            return None, None, None
        else:
            # AGGRESSIVE: Clear any existing ITI message and text before starting new trial
            self.canvas.delete("iti_message")
            self.canvas.delete("text")
            
            # Also clear by searching for all text items
            all_items = self.canvas.find_all()
            for item in all_items:
                if self.canvas.type(item) == 'text':
                    self.canvas.delete(item)
            
            # Redraw fixation before starting
            if hasattr(self, 'place_fixation_point'):
                self.place_fixation_point()
            self.image_cycle_running = True
            self.start_blend()
            return None, None, None

    def start_blend(self):
        self.update_canvas()

    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     root = tk.Tk()
#     mond_dir = os.path.join("C:", os.sep, "Users", "Admin", "Python Projects", "face_presentation", "mond_masks")
#     cycler = ImageCycler(root, mond_dir)
#     cycler.run()
