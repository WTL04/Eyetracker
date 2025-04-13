from tkinter import *
import customtkinter as ct
from PIL import Image, ImageTk, ImageSequence
import cv2
from head_track import HeadTracker
from voice import VoiceController

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

class HeadTrackerFeed(ct.CTkLabel):
    def __init__(self, master, width=400, height=300):
        super().__init__(master)
        self.tracker = HeadTracker() # add HeadTracker into this file
        self.width = width
        self.height = height
        self.use_tracking = False 
        self.update_feed()


    def update_feed(self):
        if self.use_tracking:
            frame = self.tracker.get_head_direction()
        else:
            frame = self.tracker.cap.read()[1]  # regular frame

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.width, self.height))
            image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=image)
            self.configure(image=imgtk)
            self.imgtk = imgtk
        self.after(15, self.update_feed)

    def toggle_tracking(self):
        self.use_tracking = not self.use_tracking
        return self.use_tracking 

    def stop(self):
        self.tracker.release()

# set up layout of app
root = ct.CTk()
root.geometry('880x1000')
ct.set_appearance_mode("dark")
ct.set_default_color_theme("./custom_theme.json")

# set up camera 
head_feed = HeadTrackerFeed(master=root, width=400, height=300)

# set up voice 
voice_feed = VoiceController()

# button event "Start MindControlling"
def toggle_mind_control():
    is_tracking = head_feed.toggle_tracking()
    if is_tracking:
        button1.configure(text="Stop MindControlling", fg_color="#FF0000" )
        voice_feed.start()
    else:
        button1.configure(text="Start MindControlling")
        voice_feed.stop()


# setting widget components
button1 = ct.CTkButton(
    master=root,
    width=200,
    height=80,
    text="Start MindControlling",
    font=("Noto Sans", 16),
    corner_radius=8,
    anchor="center"
    )

button1.configure(command=toggle_mind_control)


button2 =  ct.CTkButton(
    master=root,
    width=200,
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
button1.place(x=450, y=900)
button2.place(x=670, y=900)
gif_label.place(x=25, y=25)
alientalk.place(x=25,y=650)
head_feed.place(x=450,y=25)


root.mainloop()

