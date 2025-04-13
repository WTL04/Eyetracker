import sounddevice as sd
import queue
import json
import pyautogui
import signal
import sys
from vosk import Model, KaldiRecognizer

# Global flag for running
running = True

# Shutdown handler
def handle_exit(sig, frame):
    global running
    print("Shutting down voice command listener...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Vosk setup
model = Model("./models/vosk-model-small-en-us-0.15/")
recognizer = KaldiRecognizer(model, 48000)
audio_q = queue.Queue()

def start_voice_commands():
    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_q.put(bytes(indata))

    with sd.RawInputStream(samplerate=48000, blocksize=8000, dtype='int16',
                           channels=1, device=11, callback=callback):
        print("Say something (Ctrl+C to quit)")

        while running:
            try:
                data = audio_q.get(timeout=1)
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                print(f"You said: {text}")

                # Handle voice commands
                if "click" in text:
                    pyautogui.click()
                    print("CLICK command detected!")

                if "slow" in text:
                    print("SLOW command detected")

                if "scroll up" in text:
                    pyautogui.scroll(11)
                    print("Scrolling up")

                if "scroll down" in text:
                    pyautogui.scroll(-9)
                    print("Scrolling down")

    print("Voice command listener stopped.")

if __name__ == "__main__":
    start_voice_commands()


