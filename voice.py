import sounddevice as sd
import queue
import json
import pyautogui
import signal
import threading
from vosk import Model, KaldiRecognizer


class VoiceController:
    def __init__(self, model_path="./models/vosk-model-small-en-us-0.15/", device=None):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 48000)
        self.audio_q = queue.Queue()
        self.running = False
        self.device = 11  # earphone mic

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[VoiceController] Input status: {status}")
        self.audio_q.put(bytes(indata))

    def _listen_loop(self):
        print("[VoiceController] Listening for voice commands... (say 'click', 'scroll up', etc.)")

        with sd.RawInputStream(samplerate=48000, blocksize=8000, dtype='int16',
                               channels=1, device=self.device, callback=self._callback):
            while self.running:
                try:
                    data = self.audio_q.get(timeout=1)
                except queue.Empty:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    text = json.loads(result)["text"]
                    print(f"[VoiceController] Heard: {text}")
                    self._handle_command(text)

        print("[VoiceController] Voice command listener stopped.")

    def _handle_command(self, text):
        text = text.lower()
        if self.on_command:
            self.on_command(text)

        if "click" in text:
            pyautogui.click()
        elif "scroll up" in text:
            pyautogui.scroll(10)
        elif "scroll down" in text:
            pyautogui.scroll(-10)
        elif "close app" in text:
            print("CLOSE APP command received")
            if self.on_shutdown:
                self.on_shutdown()


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


