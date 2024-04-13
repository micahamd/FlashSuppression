import tkinter as tk

class FaceMenu:
    def __init__(self, root, canvas1, canvas2,callback):
        self.root = root
        self.canvas1 = canvas1
        self.canvas2 = canvas2
        self.callback = callback
        self.trial_number = None
        self.create_window()

    def get_trial_number(self):
        if not self.window.winfo_exists():
            return self.trial_number
        return int(self.trial_number_entry.get())

    def store_trial_number_and_destroy(self):
        self.trial_number = self.get_trial_number()
        self.side = 'Left' if self.switch_slider.get() == 0 else 'Right'
        self.window.destroy()
        self.callback(self.trial_number)  
        
    def create_window(self):
        self.window = tk.Toplevel(self.root)

        trial_number_label = tk.Label(self.window, text="Enter trial number (1-999):")
        trial_number_label.pack(side=tk.LEFT)

        # Entry for the trial number
        self.trial_number_entry = tk.Entry(self.window)
        self.trial_number_entry.insert(0, "60")  # Default value
        self.trial_number_entry.pack(side=tk.LEFT)

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
        ok_button = tk.Button(self.window, text="OK", command=self.store_trial_number_and_destroy)
        ok_button.pack()

    def show_window(self):
        if not self.window.winfo_exists():
            self.create_window()
        self.window.deiconify()
        self.window.wait_window()  # Wait for the window to be destroyed
        self.trial_number = self.get_trial_number()

    def get_stored_trial_number(self):
        return self.trial_number

    def pack_canvases(self, slider_value):
        side1 = tk.LEFT if int(slider_value) == 0 else tk.RIGHT
        side2 = tk.RIGHT if int(slider_value) == 0 else tk.LEFT
        self.canvas1.pack(side=side1, padx=25)
        self.canvas2.pack(side=side2, padx=25)