import cv2
import customtkinter as ct
import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk, ImageSequence
from voice import VoiceController  # <- your refactored voice class
from head_track import HeadTracker
import pyautogui

# === GUI Setup ===
root = ct.CTk()
root.title("Mind=Controlled")
root.geometry('900x1000')
ct.set_appearance_mode("dark")
ct.set_default_color_theme("./custom_theme.json")

# === Voice UI Feedback ===
mic_status_label = ct.CTkLabel(root, text="Voice: Listening...", font=("Noto Sans", 14), text_color="green")
mic_status_label.place(x=25, y=960)

command_log = ct.CTkTextbox(root, width=400, height=700)
command_log.place(x=450, y=350)
command_log.insert("0.0", "Command Log\n")
command_log.configure(state="disabled")

# === Voice Handlers ===
def handle_voice_command(text):
    command_log.configure(state="normal")
    command_log.insert("end", f"{text}\n")
    command_log.see("end")
    command_log.configure(state="disabled")

def hide_app():
    root.iconify()

def show_app():
    print("yippe")
    try:
        root.deiconify()                 # Unminimize
        root.update_idletasks()         # Make sure the window manager sees it
        root.lift()                     # Bring to front
        root.attributes('-topmost', 1)  # Force on top temporarily
        root.after(500, lambda: root.attributes('-topmost', 0))  # Restore normal stacking
        root.geometry(root.geometry())  # Force geometry reset (sometimes helps in GNOME)
    except Exception as e:
        print(f"Failed to show app: {e}")

def open_text():
    print("[GUI] Opening voice dictation popup via voice command.")
    
    # Create popup and get callbacks
    popup = tk.Toplevel(root)
    popup.geometry("600x150+600+400")
    popup.title("Voice Dictation")
    popup.configure(bg="#222")

    entry = tk.Text(popup, font=("Arial", 16), bg="#111", fg="white", insertbackground="white")
    entry.pack(expand=True, fill="both", padx=10, pady=10)

    def insert_text(text):
        entry.insert("end", text + " ")
        entry.see("end")
        entry.update()

    def on_close():
        global voice
        text = entry.get("1.0", "end").strip()
        popup.destroy()
        if text:
            pyautogui.write(text, interval=0.05)
        print("[GUI] Dictation popup closed.")

    popup.protocol("WM_DELETE_WINDOW", on_close)

    # Pass to voice controller
    voice.start_typing_mode(insert_text, on_close)

    


def shutdown_app():
    custom = tk.Toplevel(root)
    custom.title("Close App")
    custom.geometry("900x500")
    custom.configure(bg="#1f1f1f")

    msg = tk.Label(
        custom,
        text="Are you sure you want to close the app?",
        fg="white",
        bg="#1f1f1f",
        font=("Noto Sans", 28, "bold")
    )
    msg.pack(pady=40)

    def yes():
        custom.destroy()
        voice.stop()
        root.destroy()

    def no():
        custom.destroy()

    yes_btn = tk.Button(
        custom,
        text="YES",
        command=yes,
        font=("Noto Sans", 36, "bold"),
        bg="#33cc33",
        fg="white",
        activebackground="#2da82d"
    )
    yes_btn.place(relx=0.1, rely=0.4, relwidth=0.35, relheight=0.4)

    no_btn = tk.Button(
        custom,
        text="NO",
        command=no,
        font=("Noto Sans", 36, "bold"),
        bg="#cc3333",
        fg="white",
        activebackground="#a82d2d"
    )
    no_btn.place(relx=0.55, rely=0.4, relwidth=0.35, relheight=0.4)


# === Voice Controller ===
voice = VoiceController()
voice.on_command = handle_voice_command
voice.on_shutdown = shutdown_app
voice.on_hide = hide_app
voice.on_show = show_app
voice.on_text = open_text
voice.start()  # Automatically start voice control

# === HeadTracker Feed Widget ===
class HeadTrackerFeed(ct.CTkLabel):
    def __init__(self, master, width=400, height=300):
        super().__init__(master)
        self.tracker = HeadTracker()
        self.width = width
        self.height = height
        self.use_tracking = True  # Tracking is always on
        self.update_feed()

    def update_feed(self):
        if self.use_tracking:
            frame = self.tracker.get_head_direction()
        else:
            ret, frame = self.tracker.cap.read()
            if not ret:
                frame = None

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.width, self.height))
            image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=image)
            self.configure(image=imgtk)
            self.imgtk = imgtk

        self.after(15, self.update_feed)

    def stop(self):
        self.tracker.release()

# === GIF Animation ===
class AnimatedGIF(ct.CTkLabel):
    def __init__(self, master, gif_path, size):
        self.frames = []
        self.index = 0
        self.size = size

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

# === Initialize Head Tracker ===
head_feed = HeadTrackerFeed(master=root, width=400, height=300)
head_feed.place(x=450, y=25)

# === Info Text ===
alientalk = ct.CTkLabel(
    master=root,
    text=(
        "Yo, I'm the locked-in alien.\n\n"
        "I’m about to give you powers to control your computer\n"
        "with your MIND.\n\n"
        'You are now in control.\n\n'
        'Say commands like:\n'
        '• "Click"\n'
        '• "Scroll Down"\n'
        '• "Scroll Up"\n'
        '• "Close Window"\n'
        '• "Minimize Window"\n'
        '• "Maximize Window"\n'
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
alientalk.place(x=25, y=650)

gif_label = AnimatedGIF(root, "./images/lockedin.gif", size=(400, 600))
gif_label.place(x=25, y=25)

# === Launch GUI ===
root.mainloop()
