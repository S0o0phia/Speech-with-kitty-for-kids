import os
import cv2
import threading
import subprocess
from playsound import playsound

def play_sound():    
    subprocess.call(["ffplay", "-nodisp", "-autoexit", "audio.wav"])

def play_mov(name):
    cap = cv2.VideoCapture('./assets/{}.mp4'.format(name))
    command = "ffmpeg -y -i ./assets/{}.mp4 -ab 160k -ac 2 -ar 44100 -vn audio.wav".format(name)
    subprocess.call(command, shell=True)

    audio_t = threading.Thread(target=play_sound, args=())
    audio_t.start()

    while(cap.isOpened()):
        ret, frame = cap.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.IMREAD_COLOR)
        cv2.imshow('frame', gray)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    audio_t.join()
    cv2.destroyAllWindows()