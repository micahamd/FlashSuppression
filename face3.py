import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
from tkinter import PhotoImage

class ImageCanvas:
    def __init__(self, root, images,other_canvas=None, width=300, height=200):
        self.other_canvas = other_canvas
        self.canvas = tk.Canvas(root, width=width, height=height)
        self.images = images
        self.current_image_index = 0
        self.image_cycle_running = False
        self.grey_image_displayed = False
        self.grey_img = Image.open("C:/Users/Admin/Python Projects/face_presentation/grey.png")  # Open the grey image
        self.grey_img = self.grey_img.resize((width, height))  # Resize the grey image to the size of the canvas
        self.grey_img = ImageTk.PhotoImage(self.grey_img) 
        self.canvas.update()
        self.draw_checkerboard()
        self.draw_fixation_point()
        self.canvas.bind('<space>', self.handle_space_press) 

    def pack(self, side, padx=0):
        self.canvas.pack(side=side, padx=padx)
        self.canvas.update()
        self.draw_checkerboard()
        self.draw_fixation_point()

    def update_canvas(self):
        if self.image_cycle_running:
            self.canvas.create_image(0, 0, image=self.images[self.current_image_index], anchor='nw')
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.canvas.after(100, self.update_canvas)  

    def clear_canvas(self):
        self.canvas.delete("all")  # Clear the canvas
        self.grey_image_item = self.canvas.create_image(0, 0, image=self.grey_img, anchor='nw')  # Display the grey image
        self.canvas.after(1000, self.restore_image, self.current_image_index)  # Restore the paused image after 1000 ms

    def handle_space_press(self, event):
        if self.image_cycle_running:
            self.image_cycle_running = False
            self.clear_canvas()  # Clear the canvas and fill it with the grey image
            if self.other_canvas:
                self.other_canvas.clear_canvas()  # Clear the other canvas and fill it with the grey image
        else:
            self.image_cycle_running = True
            self.update_canvas()  # Start the image cycle

    def draw_checkerboard(self):
        square_size = 10
        colors = ['white', 'black']
        for i in range(0, self.canvas.winfo_width(), square_size):
            color = colors[(i // square_size) % 2]
            self.canvas.create_rectangle(i, 0, i + square_size, square_size, fill=color, outline="")
            self.canvas.create_rectangle(i, self.canvas.winfo_height() - square_size, i + square_size, self.canvas.winfo_height(), fill=color, outline="")
        for i in range(0, self.canvas.winfo_height(), square_size):
            color = colors[(i // square_size) % 2]
            self.canvas.create_rectangle(0, i, square_size, i + square_size, fill=color, outline="")
            self.canvas.create_rectangle(self.canvas.winfo_width() - square_size, i, self.canvas.winfo_width(), i + square_size, fill=color, outline="")
    
    def restore_image(self, image_index):
        self.current_image_index = image_index # Restore the saved image index
        self.grey_image_displayed = False  # Set the flag to False
        self.update_canvas() # Update the canvas
        self.draw_checkerboard()  # Redraw the checkerboard
        self.draw_fixation_point()  # Redraw the fixation point

    def draw_fixation_point(self):
        self.canvas.create_text(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, text='+', font=('Arial', 20), fill='white')

# Path to the image directory
image_dir = "C:/Users/Admin/Python Projects/face_presentation/mond_masks"

# Get a list of all jpg files in the image directory
image_files1 = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.jpg')]

# Create a Tkinter window
root = tk.Tk()

# Create a frame for the switch slider
button_frame = tk.Frame(root)
button_frame.pack()

# Create a function to pack the canvases based on the slider value
def pack_canvases(slider_value):  
    side1 = tk.LEFT if int(slider_value) == 0 else tk.RIGHT
    side2 = tk.RIGHT if int(slider_value) == 0 else tk.LEFT
    canvas1.pack(side=side1, padx=25)
    canvas2.pack(side=side2, padx=25)

# Create a label for the switch slider
switch_slider_label = tk.Label(button_frame, text="Switch direction:", fg="black")
switch_slider_label.pack(side=tk.LEFT)

# Create a scale widget
switch_slider = tk.Scale(button_frame, from_=0, to=1, orient=tk.HORIZONTAL, length=100, sliderlength=50, command=pack_canvases, showvalue=0)
switch_slider.set(0)  # Set the default value to 0 (L)
switch_slider.pack(side=tk.LEFT)


# Preload the images
image_files1 = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.jpg')]
images1 = [ImageTk.PhotoImage(Image.open(file).resize((300, 200))) for file in image_files1]

# Create the first ImageCanvas with the preloaded images
canvas1 = ImageCanvas(root, images1)

# Preload the images
image_files2 = ["C:/Users/Admin/Python Projects/face_presentation/grey.png"]
images2 = [ImageTk.PhotoImage(Image.open(file).resize((300, 200))) for file in image_files2]

# Create the second ImageCanvas with the preloaded images
canvas2 = ImageCanvas(root, images2)


# Set the other_canvas attribute of canvas1 to canvas2
canvas1.other_canvas = canvas2

# Bind the space key to the handle_space_press function for both canvases
root.bind('<space>', canvas1.handle_space_press)
# root.bind('<space>', canvas2.handle_space_press)

# Start the Tkinter event loop
root.mainloop()