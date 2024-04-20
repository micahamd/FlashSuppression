import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import json
import os

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {
            'blend_duration': 10000  # Default duration if no config file is found
        }

class Stimulus:
    RGB_CONSTANT = (145, 145, 145, 0)

    def __init__(self, image_dir, root=None):
        self.config = load_config()
        self.duration = int(self.config.get('blend_duration', 10000))
        self.image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg'))]
        self.images = [Image.open(fp).convert("RGBA").resize((200, 300)) for fp in self.image_files]
        self.root = root if root else tk.Tk()
        self.root.configure(bg='black')

        # Instead of using screen width and height, fix the canvas size
        self.canvas_width = 640
        self.canvas_height = 800
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='grey')
        self.canvas.pack(fill='both', expand=False)  # Set expand to False to keep the canvas size fixed

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

    def place_fixation_point(self):
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        self.canvas.create_text(center_x, center_y, text='+', font=('Arial', 20), fill='white')

    def blend_image(self):
        if not self.blending:
            return
        self.alpha += self.update_interval / self.duration
        if self.alpha > 1:
            self.alpha = 1
        transparent_img = Image.new("RGBA", self.images[self.current_image_index].size, self.RGB_CONSTANT)
        blended = Image.blend(transparent_img, self.images[self.current_image_index], self.alpha)
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
            reaction_time = time.time() - self.first_space_press_time
            self.first_space_press_time = None
            return self.image_y_position, self.image_path, reaction_time
        else:
            self.start_blend()
            self.first_space_press_time = time.time()
            return None, None, None

    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     stimulus = Stimulus('C:/Users/Admin/Python Projects/face_presentation/face_folder')
#     stimulus.run()
