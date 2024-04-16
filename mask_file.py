import tkinter as tk
from PIL import Image, ImageTk
import os
import time

class ImageCycler:
    MASK_CYCLE_TIME = 100  # time in milliseconds for each cycle

    def __init__(self, root, image_dir,cycle_time):
        self.root = root if root else tk.Tk()
        self.image_dir = image_dir
        self.cycle_time = cycle_time
        self.load_images()
        self.canvas = tk.Canvas(root, width=640, height=800, bg='grey')
        self.canvas.pack()
        self.current_image_index = 0
        self.image_cycle_running = False  # Changed to False initially
        self.fixation_text = self.canvas.create_text(320, 400, text='+', font=('Arial', 20), fill='white', tags="fixation")
        self.root.bind('<space>', self.handle_space_press)  # Bind space press event

    def load_images(self):
        image_files = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith('.jpg')]
        self.images = [ImageTk.PhotoImage(Image.open(fp).resize((640, 800))) for fp in image_files]

    def update_canvas(self):
        if not self.image_cycle_running:
            return
        new_image = self.canvas.create_image(10, 10, image=self.images[self.current_image_index], anchor='nw', tags="new_image")
        self.canvas.tag_raise("fixation")
        self.canvas.delete("image")
        self.canvas.itemconfig(new_image, tags="image")
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.root.after(self.MASK_CYCLE_TIME, self.update_canvas)

    def handle_space_press(self, event):
        if self.image_cycle_running:
            self.image_cycle_running = False
            self.canvas.delete("all")
            self.place_fixation_point()
            return None, None, None
        else:
            self.image_cycle_running = True
            self.start_blend()
            return None, None, None

    def place_fixation_point(self):
        self.canvas.create_text(320, 400, text='+', font=('Arial', 20), fill='white', tags="fixation")

    def start_blend(self):
        self.update_canvas()

    def run(self):
        self.root.mainloop()

# if __name__ == "__main__":
#     root = tk.Tk()
#     mond_dir = os.path.join("C:", os.sep, "Users", "Admin", "Python Projects", "face_presentation", "mond_masks")
#     cycler = ImageCycler(root, mond_dir)
#     cycler.run()
