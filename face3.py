import os
import threading
import time
import tkinter as tk
import json
from PIL import Image, ImageTk
from face_menu import FaceMenu  


# Define constants
WIDTH = 640
HEIGHT = 800
SQUARE_SIZE = 10
TRIAL_TOTAL = 60
MASK_CYCLE_TIME = .1 # 10 Hz Mondrian mask cycle time
MOND_DIR = "C:/Users/Admin/Python Projects/face_presentation/mond_masks" # Location of Mondrian masks

class ImageCanvas:
    def __init__(self, root, images,image_files, face_menu, other_canvas=None, width=WIDTH, height=HEIGHT):
        self.trial_counter = TRIAL_TOTAL  # Use the global constant TRIAL_TOTAL
        self.trial_counter_var = tk.StringVar()  # Create a StringVar to hold the trial counter value
        self.update_trial_counter_var()
        self.face_menu = face_menu
        self.other_canvas = other_canvas
        self.canvas = tk.Canvas(root, width=width, height=height)
        self.images = images
        self.image_files = image_files
        self.current_image_index = 0
        self.image_cycle_running = False
        self.grey_image_displayed = False
        self.grey_img = self.load_grey_image(width, height)
        self.canvas.update()
        self.draw_checkerboard()
        self.draw_fixation_point()
        self.canvas.bind('<space>', self.handle_space_press)
        self.start_time = None
        self.reaction_times = []

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
            new_image = self.canvas.create_image(10, 10, image=self.images[self.current_image_index][0], anchor='nw', tags="new_image")
            self.canvas.tag_raise("fixation")
            self.canvas.delete("image")
            self.canvas.itemconfig(new_image, tags="image")
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            elapsed_time = time.perf_counter() - start_time
            remaining_time = MASK_CYCLE_TIME - elapsed_time
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
            reaction_time = (time.perf_counter() - self.start_time) * 1000 # In milliseconds
            relative_path = os.path.relpath(self.images[self.current_image_index][1], start=MOND_DIR)# Relative path
            side = self.face_menu.side
            self.reaction_times.append({
                'Trial': self.trial_counter,
                'Stimulus': relative_path,  
                'RT': reaction_time,
                'Side': side
            })
            self.start_time = None
        else:
            self.image_cycle_running = True
            threading.Thread(target=self.update_canvas).start()
            self.decrement_trial_counter()  # Decrement trial counter when spacebar is pressed and image cycle is not running
            self.start_time = time.perf_counter()
            time.sleep(1)

    def save_reaction_times(self):
        with open('reaction_times.json', 'w') as f:
            json.dump(self.reaction_times, f)

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
        return [(ImageTk.PhotoImage(Image.open(file).resize((width-15, height-15))), file) for file in image_files]


def pack_canvases(slider_value, canvas1, canvas2):
    side1 = tk.LEFT if int(slider_value) == 0 else tk.RIGHT
    side2 = tk.RIGHT if int(slider_value) == 0 else tk.LEFT
    canvas1.pack(side=side1, padx=25)
    canvas2.pack(side=side2, padx=25)

def main():
    image_dir = MOND_DIR
    image_files1 = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.jpg')]
    image_files2 = ["C:/Users/Admin/Python Projects/face_presentation/grey.png"]

    root = tk.Tk()
    button_frame = tk.Frame(root)
    button_frame.pack()

    images1 = resize_images(image_files1, WIDTH, HEIGHT)
    images2 = resize_images(image_files2, WIDTH, HEIGHT)

    # Define canvas1 and canvas2 as None before they are actually defined
    canvas1 = None
    canvas2 = None

    # Define a callback function that updates the trial_counter and trial_counter_var of the ImageCanvas instance
    def update_trial_counter(trial_number):
        if canvas1 is not None:
            canvas1.trial_counter = trial_number
            canvas1.update_trial_counter_var()

    # Create a FaceMenu instance with the callback function
    face_menu = FaceMenu(root, None, None, update_trial_counter)

    # Now define canvas1 and canvas2
    canvas1 = ImageCanvas(root, images1, image_files1, face_menu)
    canvas2 = ImageCanvas(root, images2, image_files2, face_menu)

    # Update the canvases in the face_menu instance
    face_menu.canvas1 = canvas1
    face_menu.canvas2 = canvas2

    trial_counter_display = tk.Label(button_frame, textvariable=canvas1.trial_counter_var, fg="black")  # Use the StringVar as the textvariable
    trial_counter_display.pack(side=tk.LEFT)

    canvas1.other_canvas = canvas2
    root.bind('<space>', canvas1.handle_space_press)

    # Create a menu button that shows the FaceMenu window when clicked
    menu_button = tk.Button(button_frame, text="Menu", command=face_menu.show_window)
    menu_button.pack(side=tk.LEFT)

    # Store the trial number before the main Tkinter loop ends
    trial_total = face_menu.get_stored_trial_number()

    root.mainloop()
    canvas1.save_reaction_times()

    # After the mainloop ends (when the root window is closed), use the stored trial number
    global TRIAL_TOTAL
    TRIAL_TOTAL = trial_total

if __name__ == "__main__":
    main()