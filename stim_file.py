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
        super().__init__(root=root if root else tk.Tk(), image_dir=image_dir, resize_dims=(200, 300))
        self.root.configure(bg='black')
        self.current_image_index = 0
        self.blending = False
        self.alpha = 0
        self.update_interval = 50
        self.y_position = 0
        self.root.after(100, self.place_fixation_point)
        self.root.bind('<space>', self.handle_space_press)
        self.first_space_press_time = None
        self.image_y_position = None
        self.image_path = None

    def blend_image(self):
        if not self.blending:
            return
        self.alpha += self.update_interval / self.duration
        if self.alpha > 1:
            self.alpha = 1
        transparent_img = Image.new("RGBA", self.pil_images[self.current_image_index].size, self.RGB_CONSTANT)
        blended = Image.blend(transparent_img, self.pil_images[self.current_image_index], self.alpha)
        tk_img = ImageTk.PhotoImage(blended)
        center_x = self.canvas_width / 2
        self.canvas.create_image(center_x, self.y_position, anchor=tk.N, image=tk_img)
        self.canvas.image = tk_img
        self.image_y_position = self.y_position
        self.image_path = self.image_files[self.current_image_index]
        if self.alpha < 1:
            self.root.after(self.update_interval, self.blend_image)
        else:
            self.blending = False

    def start_blend(self):
        self.first_space_press_time = time.time()
        self.blending = True
        self.alpha = 0
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.y_position = random.choice([50, 450])
        self.blend_image()

    def handle_space_press(self, event):
        if self.blending:
            self.blending = False
            self.canvas.delete("all")
            self.place_fixation_point()
            if self.first_space_press_time:
                reaction_time = time.time() - self.first_space_press_time
            else:
                reaction_time = None
            self.first_space_press_time = None
            return self.image_y_position, self.image_path, reaction_time
        else:
            self.start_blend()
            return None, None, None

    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     stimulus = Stimulus('C:/Users/Admin/Python Projects/face_presentation/face_folder')
#     stimulus.run()
