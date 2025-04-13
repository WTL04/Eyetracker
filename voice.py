import os
import subprocess
import tkinter as tk
import threading
import queue
import json
import pyautogui
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pynput import mouse

class VoiceController:
    def __init__(self, model_path="./models/vosk-model-small-en-us-0.15/", device=None):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 48000)
        self.audio_q = queue.Queue()
        self.running = False
        self.device = device or None

        self.on_command = None
        self.on_shutdown = None
        self.on_hide = None
        self.on_show = None
        self.on_text = None

        self.typing_mode = False
        self.active_insert_callback = None
        self.active_close_callback = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[VoiceController] Input status: {status}")
        self.audio_q.put(bytes(indata))

    def _listen_loop(self):
        print("[VoiceController] Listening for voice commands...")

        with sd.RawInputStream(samplerate=48000, blocksize=8000, dtype='int16',
                               channels=1, device=self.device, callback=self._callback):
            while self.running:
                try:
                    data = self.audio_q.get(timeout=1)
                except queue.Empty:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"[VoiceController] Heard: {text}")
                        self._handle_command(text)

        print("[VoiceController] Voice command listener stopped.")

    def _handle_command(self, text):
        text = text.lower()

        if self.typing_mode:
            if "stop typing" in text or "close text" in text:
                print("[VoiceController] Stopping typing mode.")
                self.typing_mode = False
                if self.active_close_callback:
                    self.active_close_callback()
            elif text and self.active_insert_callback:
                self.active_insert_callback(text)
            return

        if self.on_command:
            self.on_command(text)

        if "click" in text:
            pyautogui.click()
        elif "scroll up" in text:
            pyautogui.scroll(10)
        elif "scroll down" in text:
            pyautogui.scroll(-10)
        elif "close window" in text and self.on_shutdown:
            self.on_shutdown()
        elif "minimize window" in text and self.on_hide:
            self.on_hide()
        elif "maximize window" in text and self.on_show:
            self.on_show()
        elif "open box" in text:
            print("[VoiceController] Voice command to open text triggered.")
            if self.on_text:
                self.on_text()
        elif "enter text" in text:
            pyautogui.hotKey("enter")
        elif "delete word" in text:
            pyautogui.hotKey("ctrl", "backspace")

    def start_typing_mode(self, insert_callback, close_callback):
        print("[VoiceController] Entered typing mode.")
        self.typing_mode = True
        self.active_insert_callback = insert_callback
        self.active_close_callback = close_callback

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("[VoiceController] Started voice command thread.")

    def stop(self):
        self.running = False
        print("[VoiceController] Stop signal sent.")

    def is_running(self):
        return self.running

