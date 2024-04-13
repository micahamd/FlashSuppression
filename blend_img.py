# blend_img.py
import os
from PIL import Image, ImageTk

def resize_images(image_files, width, height):
    return [(ImageTk.PhotoImage(Image.open(file).resize((width-15, height-15))), file) for file in image_files]

image_dir = "C:/Users/Admin/Python Projects/face_presentation"
image_files2 = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith('.png')]
WIDTH = 640
HEIGHT = 800
images2 = resize_images(image_files2, WIDTH, HEIGHT)