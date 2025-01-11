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
        self.root.bind('<space>', self.handle_space_press)  # Bind space press event

    def update_canvas(self):
        if not self.image_cycle_running:
            return
        # Clear the canvas before updating to prevent overlay issues
        self.canvas.delete("all")
        new_image = self.canvas.create_image(320, 400, image=self.images[self.current_image_index], anchor='center', tags="image")
        self.canvas.itemconfig(new_image, tags="image")
        self.place_fixation_point()  # Ensure the fixation point is visible
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.root.after(self.cycle_time, self.update_canvas)

    def handle_space_press(self, event):
        if self.image_cycle_running:
            self.image_cycle_running = False
            self.canvas.delete("all")
            self.place_fixation_point()
            # Show ITI message after configured delay
            self.schedule_iti_message()
            return None, None, None
        else:
            # Clear any existing ITI message before starting new trial
            self.canvas.delete("iti_message")
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
