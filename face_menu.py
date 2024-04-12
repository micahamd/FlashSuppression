import tkinter as tk

class FaceMenu:
    def __init__(self, root, canvas1, canvas2):
        self.window = tk.Toplevel(root)
        self.canvas1 = canvas1
        self.canvas2 = canvas2

              
        # Switch slider label
        switch_slider_label = tk.Label(self.window, text="Switch target:", fg="black")
        switch_slider_label.pack(side=tk.LEFT)

        # Label for the left anchor of the slider
        left_label = tk.Label(self.window, text="Left")
        left_label.pack(side=tk.LEFT)
 
        self.switch_slider = tk.Scale(self.window, from_=0, to=1, orient=tk.HORIZONTAL, length=100, sliderlength=50, command=self.pack_canvases, showvalue=0)
        self.switch_slider.set(0)
        self.switch_slider.pack(side=tk.LEFT)

        # Label for the right anchor of the slider
        right_label = tk.Label(self.window, text="Right")
        right_label.pack(side=tk.LEFT)

        # Create an 'OK' button that destroys the window when clicked
        ok_button = tk.Button(self.window, text="OK", command=self.window.destroy)
        ok_button.pack()

    def pack_canvases(self, slider_value):
        side1 = tk.LEFT if int(slider_value) == 0 else tk.RIGHT
        side2 = tk.RIGHT if int(slider_value) == 0 else tk.LEFT
        self.canvas1.pack(side=side1, padx=25)
        self.canvas2.pack(side=side2, padx=25)