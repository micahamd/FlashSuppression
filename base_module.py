import tkinter as tk
from PIL import Image, ImageTk
import os
import json

def load_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {}

class BaseModule:
    RGB_CONSTANT = (145, 145, 145, 0)

    def __init__(self, root, image_dir, canvas_width=640, canvas_height=800, resize_dims=None):
        self.root = root
        self.image_dir = image_dir
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.resize_dims = resize_dims
        self.images = self.load_images()
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg='grey')
        self.canvas.pack(fill='both', expand=False)
        self.place_fixation_point()

    def load_images(self):
        image_files = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg'))]
        self.image_files = image_files
        if self.resize_dims:
            self.pil_images = [Image.open(fp).convert("RGBA").resize(self.resize_dims) for fp in image_files]
            return [ImageTk.PhotoImage(img) for img in self.pil_images]
        else:
            self.pil_images = [Image.open(fp).convert("RGBA") for fp in image_files]
            return [ImageTk.PhotoImage(img) for img in self.pil_images]

    def place_fixation_point(self):
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        self.canvas.create_text(center_x, center_y, text='+', font=('Arial', 20), fill='white')
