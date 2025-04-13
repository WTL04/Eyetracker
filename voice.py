import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

# Setup
model = Model("./vosk-model-small-en-us-0.15/")  # path to your Vosk model
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
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                print(f"You said: {text}")

                if "click" in text:
                    print("CLICK command detected!")


