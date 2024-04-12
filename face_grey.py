import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import time
import os
import random

# Get a list of all the PNG files in the directory
image_dir = 'C:/Users/Admin/Python Projects/face_presentation/face_folder'
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith('.png')]

# Initialize the image index
image_index = 0

# Create the main window
root = tk.Tk()
root.configure(bg='black')

# Create a frame to hold the START button, switch slider and transition time
button_frame = tk.Frame(root)
button_frame.pack()

# Open the first image file
img = Image.open(image_files[image_index])
img = img.convert("RGBA")
img = img.resize((200, 300))

# Create a blank image for the initial display
blank_img = Image.new('RGBA', (200, 300), (0, 0, 0, 0))

# Convert the Image object to a Tkinter PhotoImage object
tk_img = ImageTk.PhotoImage(blank_img)

# Create a frame to hold the canvases
frame = tk.Frame(root,background='black',width=1600,height=1000)
frame.pack()
frame.pack_propagate(0)  # Don't allow the widgets inside to determine the frame's width / height

def draw_checkerboard(canvas):
    square_size = 10  # Size of each square in the checkerboard
    colors = ['white', 'black']  # Colors for the checkerboard

    # Draw the top and bottom borders
    for i in range(0, 640, square_size):
        color = colors[(i // square_size) % 2]
        canvas.create_rectangle(i, 0, i + square_size, square_size, fill=color, outline="")
        canvas.create_rectangle(i, 800 - square_size, i + square_size, 800, fill=color, outline="")

    # Draw the left and right borders
    for i in range(0, 800, square_size):
        color = colors[(i // square_size) % 2]
        canvas.create_rectangle(0, i, square_size, i + square_size, fill=color, outline="")
        canvas.create_rectangle(640 - square_size, i, 640, i + square_size, fill=color, outline="")

# Create the first canvas
canvas1 = tk.Canvas(frame, width=640, height=800, bg='grey')
canvas1.pack(side=tk.LEFT, padx=25)  # Pack on the left side of the frame with 25 px padding

# Get a list of all JPG files in the directory
image_files2 = [f for f in os.listdir("C:/Users/Admin/Python Projects/face_presentation/mond_masks") if f.endswith('.jpg')]

# Initialize the image index
image_index2 = 0

# Preload all the images
images2 = []
for image_file in image_files2:
    img2 = Image.open("C:/Users/Admin/Python Projects/face_presentation/mond_masks/" + image_file)
    img2 = img2.resize((640, 800))
    tk_img2 = ImageTk.PhotoImage(img2)
    images2.append(tk_img2)

# Create the second canvas
canvas2 = tk.Canvas(frame, width=640, height=800, bg='grey')
canvas2.pack(side=tk.RIGHT, padx=25)  # Pack on the right side of the frame with 25 px padding

# Display the first image on canvas2
image_on_canvas2 = canvas2.create_image(0, 0, anchor='nw', image=images2[image_index2])

# Create a global variable to store the ID of the scheduled task
scheduled_task = None

# Create a blank image for canvas2
blank_image = Image.new('RGB', (640, 800))
blank_tk_image = ImageTk.PhotoImage(blank_image)
image_on_canvas2 = canvas2.create_image(0, 0, anchor='nw', image=blank_tk_image)

import threading
import time

# Global flag to track whether the image cycle is running or not
image_cycle_running = False

import queue

# Create a queue
image_queue = queue.Queue()

def change_image():
    global image_index2, image_on_canvas2, scheduled_task, image_cycle_running
    start_time = time.time()  # Record the start time
    image_index2 = (image_index2 + 1) % len(images2)
    # Put the new image into the queue
    image_queue.put(images2[image_index2])
    execution_time = time.time() - start_time  # Calculate the execution time
    delay = max(.5 - execution_time, 0)  # Calculate the delay for the next call
    scheduled_task = threading.Timer(delay, change_image)  # Schedule the next image change
    scheduled_task.start()
    image_cycle_running = True  # Set the flag to True

class ImageQueueChecker:
    def __init__(self, root, canvas2, image_on_canvas2):
        self.root = root
        self.canvas2 = canvas2
        self.image_on_canvas2 = image_on_canvas2
        self.check_queue()

    def check_queue(self):
        try:
            # Get the new image from the queue
            new_image = image_queue.get_nowait()
        except queue.Empty:
            # No new image in the queue
            pass
        else:
            # Update the image on canvas2
            self.canvas2.itemconfig(self.image_on_canvas2, {'image': new_image})
            draw_checkerboard(self.canvas2)  # Redraw the checkerboard
        # Schedule the next call to check_queue
        self.root.after(100, self.check_queue)

# Start checking the queue
checker = ImageQueueChecker(root, canvas2, image_on_canvas2)

# Function to stop the image cycling
def stop_image_cycle():
    global scheduled_task, image_cycle_running
    if scheduled_task is not None:
        scheduled_task.cancel()
        scheduled_task = None
    image_cycle_running = False  # Set the flag to False

# Function to pack the canvases and blend the image
def start():
    pack_canvases()
    if not image_cycle_running:  # Only start the image cycle if it's not already running
        change_image()
    blend_image()

# Function to clear the canvas
def clear_canvas():
    canvas1.delete("all")
    draw_checkerboard(canvas1)
    canvas1.create_text(320, 400, text='+', font=('Arial', 20), fill='white')
 
# Add a fixation point in the center of the canvas
canvas2.create_text(320, 400, text='+', font=('Arial', 20), fill='white')

# Calculate the number of top and bottom presentations
num_images = len(image_files)
num_top = num_images // 2
num_bottom = num_images - num_top

# Create a list of y_positions with an equal number of top and bottom positions
y_positions = [0]*num_top + [800 - 300]*num_bottom

random.shuffle(y_positions) # Shuffle the list to randomize the order
y_position = y_positions.pop()  # Get the first y_position

# Adjust the y_position if the image is at the bottom
if y_position == 800 - 300:
    y_position -= 300

# Position the image at the top center or bottom center of the canvas randomly
canvas1.create_image(320, y_position, anchor=tk.N, image=tk_img)  

blending = False # Flag to indicate whether the blending process is running
space_pressed = False # Flag to indicate whether the SPACEBAR is pressed

# Add a new global variable to store the onset time
onset_time = None

image_id = None
    
# Create a new global variable to store the trial count
trial_count_var = tk.IntVar(value=2)

# Create a label for the trial count spinbox
trial_count_label = tk.Label(button_frame, text="Trial count:", fg="black")
trial_count_label.pack(side=tk.LEFT)

# Create a Spinbox widget for the trial count
trial_count_spinbox = tk.Spinbox(button_frame, from_=2, to=100, textvariable=trial_count_var)
trial_count_spinbox.pack(side=tk.LEFT)

def load_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        img = img.resize((200, 300))
        return img
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

# Define img as a global variable and load an image
img = load_image(image_files[0])

if img is None:
    print("Image not loaded.")
else:
    # Define transparent_img as a global variable
    transparent_img = img.copy()
    transparent_img.putalpha(0)

def blend_image(i=0):
    global img, tk_img, blending, space_pressed, onset_time, image_id, transparent_img, image_index, image_files
    blend_duration = blend_duration_var.get()
    if i == 0:
        # Update the image to be displayed
        img = load_image(image_files[image_index])
        # Assuming the background is grey (192, 192, 192)
        transparent_img = Image.new("RGBA", img.size, (192, 192, 192, 0))  
        # Remaining code
        blend_duration_spinbox.config(state="disabled")
        button.config(state="disabled")
        rt_label.config(text="")
        onset_time = time.time() * 1000
        space_pressed = False
        if blending:
            return
        blending = True
        tk_img = ImageTk.PhotoImage(transparent_img)
        if image_id:
            canvas1.delete(image_id)
        image_id = canvas1.create_image(320, y_position, anchor=tk.N, image=tk_img)  # Moved this line here
    if space_pressed:
        blending = False
        clear_canvas()
        return
    if i >= blend_duration:
        # If blending is over, just keep the image on the screen
        return
    alpha = i / blend_duration
    blended = Image.blend(transparent_img, img, alpha)
    tk_img = ImageTk.PhotoImage(blended)
    if image_id:
        canvas1.delete(image_id)
    draw_checkerboard(canvas1)
    canvas1.create_text(320, 400, text='+', font=('Arial', 20), fill='white')
    image_id = canvas1.create_image(320, y_position, anchor=tk.N, image=tk_img)
    root.update()
    root.after(int(1000 * 0.01), blend_image, i+1)

def reset_image(from_space_press=False):
    global img, tk_img, blending, image_index, y_positions, y_position, transparent_img 
    blend_duration_spinbox.config(state="normal")  # Enable the Spinbox
    button.config(state="normal")  # Re-enable the START button
    blending = False  # Clear the blending flag
    image_index = (image_index + 1) % len(image_files)  # Move to the next image, looping back to the first image if necessary
    img = load_image(image_files[image_index])
    if from_space_press:
        # Create a fully transparent image for the initial display
        transparent_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
        tk_img = ImageTk.PhotoImage(transparent_img)
    else:
        tk_img = ImageTk.PhotoImage(img)
    canvas1.create_image(320, y_position, anchor=tk.N, image=tk_img)
    # Get the next y_position
    y_position = y_positions.pop() if y_positions else 0  # Default to 0 if y_positions is empty
    canvas1.create_image(320, y_position, anchor=tk.N, image=tk_img)
    onset_time = None  # Reset the onset_time variable

    # Decrement the trial count and start a new trial if there are remaining trials
    trial_count_var.set(trial_count_var.get() - 1)  # Use trial_count_var instead of trial_count
    if trial_count_var.get() > 0:  # Use trial_count_var instead of trial_count
        root.after(1000, start)  # Start a new trial after 1000 ms
    else:
        # Stop the image cycling if it's the last trial
        stop_image_cycle()
            
# Create a label for the reaction time with white text
rt_label = tk.Label(root, text="", fg="black")
rt_label.place(x=750, y=40)  # Place the label at the coordinates 

# Function to handle the SPACEBAR press
def handle_space_press(event):
    global space_pressed, onset_time, scheduled_task
    space_pressed = True
    if onset_time is not None:
        rt = time.time() * 1000 - onset_time
        rt_label.config(text=f"Reaction Time: {rt:.2f} ms")
        root.after(1000, lambda: reset_image(True))  # Call reset_image() before clear_canvas()
        root.after(1000, clear_canvas)  # Schedule clear_canvas() to be called after reset_image()     
    else:
        root.after(1000, lambda: reset_image(True))  # Schedule reset_image() to be called before clear_canvas()
        root.after(1000, clear_canvas)  # Schedule clear_canvas() to be called after a delay
        
# Bind the SPACEBAR to the handle_space_press function
root.bind('<space>', handle_space_press)

# Create a function to pack the canvases based on the slider value
def pack_canvases():  
    side1 = tk.LEFT if switch_slider.get() == 0 else tk.RIGHT
    side2 = tk.RIGHT if switch_slider.get() == 0 else tk.LEFT
    canvas1.pack(side=side1, padx=25)
    canvas2.pack(side=side2, padx=25)
   
# Create a new global variable to store the blend duration
blend_duration_var = tk.IntVar(value=5000)

# Create a label for the switch slider
switch_slider_label = tk.Label(button_frame, text="Transition time (ms):", fg="black")
switch_slider_label.pack(side=tk.LEFT)

# Create a Spinbox widget for the blend duration
blend_duration_spinbox = tk.Spinbox(button_frame, from_=1000, to=20000, textvariable=blend_duration_var)
blend_duration_spinbox.pack(side=tk.LEFT)

# Create the START button and pack it into the button_frame
button = tk.Button(button_frame, text="START", command=start)
button.pack(side=tk.LEFT)

# Create a variable to hold the value of the scale
scale_value = tk.StringVar()
scale_value.set("L")  # Set the default value to "L"

# Update the value of scale_value when the scale is moved
def update_scale_value(val):
    scale_value.set("R" if float(val) > 0 else "L")

# Everything terminates cleanly when the window is closed
def cleanup():
    global image_cycle_running, scheduled_task
    # Stop the image cycle
    image_cycle_running = False
    if scheduled_task is not None:
        scheduled_task.cancel()
    # Close the window
    root.destroy()

# Call cleanup when the window is closed
root.protocol("WM_DELETE_WINDOW", cleanup)

# Create a scale widget
switch_slider = tk.Scale(button_frame, from_=0, to=1, orient=tk.HORIZONTAL, length=100, sliderlength=50, command=update_scale_value, showvalue=0)
switch_slider.set(0)  # Set the default value to 0 (L)
switch_slider.pack(side=tk.LEFT)

# Create a label to display the value of the scale
scale_label = tk.Label(button_frame, textvariable=scale_value)
scale_label.pack(side=tk.LEFT)

# Start the Tkinter event loop
root.mainloop()