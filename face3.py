import os
import threading
import time
import tkinter as tk
from PIL import Image, ImageTk
from face_menu import FaceMenu  


# Define constants
WIDTH = 640
HEIGHT = 800
SQUARE_SIZE = 10


class ImageCanvas:
    def __init__(self, root, images, other_canvas=None, width=WIDTH, height=HEIGHT):
        self.trial_counter = 60
        self.trial_counter_var = tk.StringVar()  # Create a StringVar to hold the trial counter value
        self.update_trial_counter_var()
        self.other_canvas = other_canvas
        self.canvas = tk.Canvas(root, width=width, height=height)
        self.images = images
        self.current_image_index = 0
        self.image_cycle_running = False
        self.grey_image_displayed = False
        self.grey_img = self.load_grey_image(width, height)
        self.canvas.update()
        self.draw_checkerboard()
        self.draw_fixation_point()
        self.canvas.bind('<space>', self.handle_space_press)

    @staticmethod
    def load_grey_image(width, height):
        grey_img = Image.open("C:/Users/Admin/Python Projects/face_presentation/grey.png")
        grey_img = grey_img.resize((width-15, height-15))
        return ImageTk.PhotoImage(grey_img)
    
    def update_trial_counter_var(self):
        self.trial_counter_var.set(f'Trial counter: {self.trial_counter}')

    def pack(self, side, padx=0):
        self.canvas.pack(side=side, padx=padx)
        self.canvas.update()
        self.draw_checkerboard()
        self.draw_fixation_point()

    def update_canvas(self):
        start_time = time.perf_counter()
        while self.image_cycle_running:
            new_image = self.canvas.create_image(10, 10, image=self.images[self.current_image_index], anchor='nw', tags="new_image")
            self.canvas.tag_raise("fixation")
            self.canvas.delete("image")
            self.canvas.itemconfig(new_image, tags="image")
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            elapsed_time = time.perf_counter() - start_time
            remaining_time = 0.1 - elapsed_time
            if remaining_time > 0:
                time.sleep(remaining_time)
            start_time = time.perf_counter()
            
    def clear_canvas(self):
        self.canvas.delete("image")
        self.grey_image_item = self.canvas.create_image(10, 10, image=self.grey_img, anchor='nw', tags="image")
        self.canvas.tag_raise("fixation")
        self.canvas.after(1000, self.restore_image, self.current_image_index)

    def decrement_trial_counter(self):
        if self.trial_counter > 0:
            self.trial_counter -= 1
            self.update_trial_counter_var()  # Update the StringVar when the trial counter is decremented

    def handle_space_press(self, event):
        if self.image_cycle_running:
            self.image_cycle_running = False
            self.clear_canvas()
            if self.other_canvas:
                self.other_canvas.clear_canvas()
        else:
            self.image_cycle_running = True
            threading.Thread(target=self.update_canvas).start()
            self.decrement_trial_counter()  # Decrement trial counter when spacebar is pressed and image cycle is not running

    def draw_checkerboard(self):
        square_size = SQUARE_SIZE
        colors = ['white', 'black']
        for i in range(0, self.canvas.winfo_width(), square_size):
            color = colors[(i // square_size) % 2]
            self.canvas.create_rectangle(i, 0, i + square_size, square_size, fill=color, outline="", tags="checkerboard")
            self.canvas.create_rectangle(i, self.canvas.winfo_height() - square_size, i + square_size, self.canvas.winfo_height(), fill=color, outline="", tags="checkerboard")
        for i in range(0, self.canvas.winfo_height(), square_size):
            color = colors[(i // square_size) % 2]
            self.canvas.create_rectangle(0, i, square_size, i + square_size, fill=color, outline="", tags="checkerboard")
            self.canvas.create_rectangle(self.canvas.winfo_width() - square_size, i, self.canvas.winfo_width(), i + square_size, fill=color, outline="", tags="checkerboard")

    def restore_image(self, image_index):
        self.current_image_index = image_index
        self.grey_image_displayed = False
        if self.image_cycle_running:
            threading.Thread(target=self.update_canvas).start()

    def draw_fixation_point(self):
        self.canvas.create_text(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, text='+', font=('Arial', 20), fill='white', tags="fixation")


def resize_images(image_files, width, height):
    return [ImageTk.PhotoImage(Image.open(file).resize((width-15, height-15))) for file in image_files]


def pack_canvases(slider_value, canvas1, canvas2):
    side1 = tk.LEFT if int(slider_value) == 0 else tk.RIGHT
    side2 = tk.RIGHT if int(slider_value) == 0 else tk.LEFT
    canvas1.pack(side=side1, padx=25)
    canvas2.pack(side=side2, padx=25)


def main():
    image_dir = "C:/Users/Admin/Python Projects/face_presentation/mond_masks"
    image_files1 = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.jpg')]
    image_files2 = ["C:/Users/Admin/Python Projects/face_presentation/grey.png"]

    root = tk.Tk()
    button_frame = tk.Frame(root)
    button_frame.pack()

    images1 = resize_images(image_files1, WIDTH, HEIGHT)
    canvas1 = ImageCanvas(root, images1)

    trial_counter_display = tk.Label(button_frame, textvariable=canvas1.trial_counter_var, fg="black")  # Use the StringVar as the textvariable
    trial_counter_display.pack(side=tk.LEFT)

    images2 = resize_images(image_files2, WIDTH, HEIGHT)
    canvas2 = ImageCanvas(root, images2)

    canvas1.other_canvas = canvas2
    root.bind('<space>', canvas1.handle_space_press)

    # Create a menu button that opens the FaceMenu window when clicked
    menu_button = tk.Button(button_frame, text="Menu", command=lambda: FaceMenu(root, canvas1, canvas2))
    menu_button.pack(side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    main()