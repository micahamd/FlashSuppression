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

    def __init__(self, root, image_dir, canvas_width=640, canvas_height=800, resize_dims=None, with_border=True):
        self.root = root
        self.image_dir = image_dir
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.resize_dims = resize_dims
        self.config = load_config()
        self.iti_delay = self.config.get('iti_message_delay', 500)  # Default to 500ms if not in config
        self.iti_message_text = self.config.get('iti_message_text', 'Press SPACE to continue')  # Default message
        self.canvas_bg_color = self.config.get('canvas_bg_color', '#808080')  # Default to standard grey if not in config
        self.images = self.load_images()

        # Create a frame to hold the canvas and border
        self.frame = tk.Frame(self.root, bg='black')
        self.frame.pack(fill='both', expand=True)

        # Create the canvas with the checkerboard border
        if with_border:
            # Calculate the total canvas size including border
            border_width = 60  # Border width in pixels
            total_width = self.canvas_width + (border_width * 2)
            total_height = self.canvas_height + (border_width * 2)

            # Create a canvas that includes both content area and border
            self.canvas = tk.Canvas(self.frame, width=total_width, height=total_height, bg='black', highlightthickness=0)
            # Center the canvas in the frame
            self.canvas.pack(side='top', anchor='center', expand=True, padx=50, pady=50)

            # Draw the checkerboard border
            self.draw_checkerboard_border(border_width)

            # Create a content area in the center
            self.content_area = self.canvas.create_rectangle(
                border_width, border_width,
                border_width + self.canvas_width, border_width + self.canvas_height,
                fill=self.canvas_bg_color, outline=''
            )
        else:
            # Create a simple canvas without border
            self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height, bg=self.canvas_bg_color)
            # Center the canvas in the frame
            self.canvas.pack(side='top', anchor='center', expand=True, padx=50, pady=50)

        self.place_fixation_point()

    def load_images(self):
        if not os.path.exists(self.image_dir):
            raise FileNotFoundError(f"Image directory not found: {self.image_dir}")

        image_files = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg'))]
        if not image_files:
            raise ValueError(f"No image files found in directory: {self.image_dir}")

        self.image_files = image_files
        if self.resize_dims:
            self.pil_images = [Image.open(fp).convert("RGBA").resize(self.resize_dims) for fp in image_files]
            return [ImageTk.PhotoImage(img) for img in self.pil_images]
        else:
            self.pil_images = [Image.open(fp).convert("RGBA") for fp in image_files]
            return [ImageTk.PhotoImage(img) for img in self.pil_images]

    def draw_checkerboard_border(self, border_width, square_size=20):
        """Draw a checkerboard pattern in the border area of the canvas"""
        # Use the total canvas dimensions including border
        total_width = self.canvas_width + (border_width * 2)
        total_height = self.canvas_height + (border_width * 2)

        # Clear any existing checkerboard
        self.canvas.delete("checkerboard")

        # Draw checkerboard pattern in the border area
        for i in range(0, total_width, square_size):
            for j in range(0, total_height, square_size):
                # Only draw if in the border area (not in the content area)
                if (i < border_width or i >= border_width + self.canvas_width or
                    j < border_width or j >= border_width + self.canvas_height):
                    # Alternate colors based on position
                    color = "white" if (i // square_size + j // square_size) % 2 == 0 else "black"
                    self.canvas.create_rectangle(
                        i, j, i + square_size, j + square_size,
                        fill=color, outline="", tags="checkerboard"
                    )

    def place_fixation_point(self):
        # If we have a border, adjust the center position
        if hasattr(self, 'content_area'):
            border_width = 60
            center_x = border_width + (self.canvas_width / 2)
            center_y = border_width + (self.canvas_height / 2)
        else:
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2

        self.canvas.create_text(center_x, center_y, text='+', font=('Arial', 20), fill='white')

    def show_iti_message(self):
        # Record the time when ITI message is shown (for reaction time calculation)
        import time
        if hasattr(self, 'root') and hasattr(self.root, 'iti_start_time'):
            self.root.iti_start_time[0] = time.time()
        
        # If we have a border, adjust the center position
        if hasattr(self, 'content_area'):
            border_width = 60
            center_x = border_width + (self.canvas_width / 2)
            center_y = border_width + (self.canvas_height / 2) + 50  # Place below fixation point
        else:
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2 + 50  # Place below fixation point

        self.canvas.create_text(center_x, center_y, text=self.iti_message_text,
                              font=('Arial', 16), fill='white', tags='iti_message')

    def schedule_iti_message(self):
        """Schedule the ITI message to appear after the configured delay"""
        # Cancel any existing scheduled ITI message first
        if hasattr(self, 'iti_after_id') and self.iti_after_id:
            try:
                self.root.after_cancel(self.iti_after_id)
            except:
                pass
        # Schedule new ITI message and store the ID
        self.iti_after_id = self.root.after(self.iti_delay, self.show_iti_message)
    
    def cancel_iti_message(self):
        """Cancel any pending ITI message"""
        if hasattr(self, 'iti_after_id') and self.iti_after_id:
            try:
                self.root.after_cancel(self.iti_after_id)
                self.iti_after_id = None
            except:
                pass
