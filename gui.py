from tkinter import *
import customtkinter as ct
from PIL import Image, ImageTk, ImageSequence
import cv2

# WHAT THE FLIP IS THIS
class AnimatedGIF(ct.CTkLabel):
    def __init__(self, master, gif_path, size):
        self.frames = []
        self.index = 0
        self.size = size

        # Load GIF frames
        im = Image.open(gif_path)
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            frame = frame.resize(self.size, Image.Resampling.LANCZOS)
            self.frames.append(ImageTk.PhotoImage(frame))

        super().__init__(master, image=self.frames[0], text="")
        self.after(100, self.animate)

    def animate(self):
        self.index = (self.index + 1) % len(self.frames)
        self.configure(image=self.frames[self.index])
        self.after(100, self.animate)

# enable webcam
class WebcamViewer(ct.CTkLabel):
    def __init__(self, master):
        super().__init__(master)
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((320, 240))
            imgtk = ImageTk.PhotoImage(image=img)
            self.configure(image=imgtk)
            self.imgtk = imgtk  # prevent garbage collection

        self.after(15, self.update_frame)


# set up layout of app
root = ct.CTk()
root.geometry('900x1000')
ct.set_appearance_mode("dark")
ct.set_default_color_theme("./custom_theme.json")

# set up camera 
viewer = WebcamViewer(root)

# setting widget components
button1 = ct.CTkButton(
    master=root,
    width=50,
    height=80,
    text="Start MindControlling",
    font=("Noto Sans", 16),
    corner_radius=8,
    anchor="center"
    )
button2 =  ct.CTkButton(
    master=root,
    width=170,
    height=80,
    text="Hide Me",
    font=("Noto Sans", 16), 
    corner_radius=8,
    anchor="center"
    )

alientalk = ct.CTkLabel(
    master=root,
    text=(
        "Yo, I'm the locked-in alien.\n\n"
        "I’m about to give you powers to control your computer\n"
        "with your MIND.\n\n"
        'Click the "Start MindControlling" button to begin.\n\n'
        'Say commands like:\n'
        '• "Click"\n'
        '• "Scroll Down"\n'
        '• "Scroll Up"\n'
        "to interact with your computer."
    ),
    width=400,
    height=330,
    fg_color="#333333",
    text_color="white",
    font=("Noto Sans", 16),
    corner_radius=12,
    anchor="w",
    justify="left"
)

# locked in alien
gif_label = AnimatedGIF(root, "./images/lockedin.gif", size=(400,600))
gif_label.pack(pady=20)



# placing widgets
button1.place(x=500, y=900)
button2.place(x=700, y=900)
gif_label.place(x=25, y=25)
alientalk.place(x=25,y=650)
viewer.place(x=500,y=500)

root.mainloop()

