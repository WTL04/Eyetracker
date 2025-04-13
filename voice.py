import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

# Setup
model = Model("model")  # path to your Vosk model
recognizer = KaldiRecognizer(model, 16000)
audio_q = queue.Queue()

# Record audio callback
def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_q.put(bytes(indata))

# Start listening
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎤 Say something (Ctrl+C to quit)")

    while True:
        data = audio_q.get()
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result)["text"]
            print(f"🗣️ You said: {text}")

            # Trigger something:
            if "click" in text:
                print("💥 CLICK command detected!")
