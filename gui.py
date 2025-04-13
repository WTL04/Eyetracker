from tkinter import *
import customtkinter as ct
from PIL import Image, ImageTk

from PIL import Image, ImageTk, ImageSequence

# WHAT THE FLIP IS THIS
class AnimatedGIF(ct.CTkLabel):
    def __init__(self, master, gif_path):
        self.frames = []
        self.index = 0

        # Load GIF frames
        im = Image.open(gif_path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            self.frames.append(ImageTk.PhotoImage(frame))

        super().__init__(master, image=self.frames[0], text="")
        self.after(100, self.animate)

    def animate(self):
        self.index = (self.index + 1) % len(self.frames)
        self.configure(image=self.frames[self.index])
        self.after(100, self.animate)

# set up layout of app
root = ct.CTk()
root.geometry('800x1000')
ct.set_appearance_mode("dark")
ct.set_default_color_theme("./custom_theme.json")

# setting widget components
button1 = ct.CTkButton(master=root, text="Start MindControlling")
button2 = ct.CTkButton(master=root, text="Hide Me")

# locked in alien
gif_label = AnimatedGIF(root, "./images/lockedin.gif")
gif_label.pack(pady=20)



# placing widgets
button1.place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop()

