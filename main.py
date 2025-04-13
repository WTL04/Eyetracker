import subprocess
import time
import signal

def main():

    print("Launching head_track.py...")
    p2 = subprocess.Popen(["python", "head_track.py"])
     
    print("Launching voice.py...")
    p1 = subprocess.Popen(["python", "voice.py"])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCaught Ctrl+C! Terminating subprocesses...")
        p1.kill()
        p2.kill()
        p1.wait()
        p2.wait()
        print("All subprocesses terminated.")

if __name__ == "__main__":
    main()
