import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import time

# Set the blend duration
blend_duration = 500  # Increase this for a longer transition

# Open the image file
img = Image.open('C:/Users/Admin/Python Projects/face_presentation/fha1.png')
img = img.convert("RGBA")

# Resize the image
img = img.resize((200, 300))

# Create the main window
root = tk.Tk()
root.configure(bg='grey')

# Convert the Image object to a Tkinter PhotoImage object
tk_img = ImageTk.PhotoImage(img)

# Create a canvas for the image
canvas = tk.Canvas(root, width=640, height=800,bg='grey')
canvas.pack()

# Add the image to the canvas
canvas.create_image(320, 0, anchor=tk.N, image=tk_img)  # Position the image at the top center of the canvas


# Flag to indicate whether the blending process is running
blending = False

# Function to blend the image
def blend_image():
    global img, tk_img, blending  # Make sure we're modifying the global img, tk_img, and blending variables
    if blending:
        return  # Return immediately if the blending process is running
    blending = True  # Set the blending flag
    background_color = root.cget('bg')  # Get the background color of the root window
    background = Image.new('RGBA', img.size, background_color)
    for i in range(blend_duration):
        if not blending:  # Check the blending flag
            break  # Break the loop if blending is False
        alpha = i / blend_duration
        blended = Image.blend(img, background, alpha)
        img = blended  # Update the img variable
        tk_img = ImageTk.PhotoImage(img)  # Create a new PhotoImage object
        canvas.create_image(320, 0, anchor=tk.N, image=tk_img)
        root.update()
        time.sleep(0.01)  # Decrease this for a smoother transition
    blending = False  # Clear the blending flag
    root.after(100, reset_image)  # Reset the image 100 ms after the blend duration passes

# Function to reset the image
def reset_image():
    global img, tk_img, blending  # Make sure we're modifying the global img, tk_img, and blending variables
    blending = False  # Clear the blending flag
    img = Image.open('C:/Users/Admin/Python Projects/face_presentation/fha1.png')
    img = img.convert("RGBA")
    img = img.resize((200, 300))
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(320, 0, anchor=tk.N, image=tk_img)

# Bind the SPACEBAR to the reset_image function
root.bind('<space>', lambda event: reset_image())

# Create the START button
button = tk.Button(root, text="START", command=blend_image)
button.pack()

# Start the Tkinter event loop
root.mainloop()