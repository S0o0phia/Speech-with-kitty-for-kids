import os
import cv2
import videos
import argparse
import threading
import sounddevice
import tkinter as tk
import PIL.Image, PIL.ImageTk
from predictor import Predictor
from scipy.io.wavfile import write

count = 0

class App:
    def __init__(self, window, window_title, opts, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.ok=False

        self.model = Predictor(opts)

        self.ear = cv2.imread('assets/ear.png')
        self.ear = cv2.resize(self.ear, (300, 300), interpolation = cv2.INTER_CUBIC)
        
        self.timer=()
        self.vid = VideoCapture(self.video_source)
        
        self.audio_t = threading.Thread(target=self.audio_recording, args=())

        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()

        self.btn_start=tk.Button(window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.LEFT)

        self.delay = 10
        self.update()

        self.window.mainloop()

    def startTimer(self):
        global count
        count += 1
        timer = threading.Timer(1, self.startTimer)
        timer.start()

        if count == 5:
            self.close_camera()
            timer.cancel()

    def audio_recording(self):
        fs = 16000
        record_voice = sounddevice.rec(int(5 * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write("output.wav", fs, record_voice)
        count = 0

    def open_camera(self):
        self.ok = True
        print("camera opened => Recording Start ...")
        self.startTimer()
        self.audio_t.start()

    def close_camera(self):
        self.ok = False
        print("camera closed => Recording Stopped")
        args = self.vid.args
        print(args.name[0] + '.' + args.type[0])
        video, _ = videos.load_video('./' + args.name[0] + '.' + args.type[0])
        print(self.model.predict(video))

    def update(self):
        ret, frame = self.vid.get_frame()
        frame_show = frame

        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            h, w, c = self.ear.shape
            fh = 720 - h
            roi = frame_show[fh : fh + h, 0 : w]
            frame_show[fh : fh + h, 0 : w] = self.ear  

        if ret:
            frame_show = cv2.resize(frame_show, (440, 280))
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_show))
            self.canvas.create_image(800, 450, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay, self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.args = CommandLineParser().args
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.fourcc = VIDEO_TYPE[self.args.type[0]]

        STD_DIMENSIONS =  {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }

        res = STD_DIMENSIONS[self.args.res[0]]
        print(self.args.name, self.fourcc,res)
        self.out = cv2.VideoWriter(self.args.name[0] + '.' + self.args.type[0] , self.fourcc , 29.97, res)

        self.vid.set(3, res[0])
        self.vid.set(4, res[1])
        self.width,self.height=res

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret: return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:   return (ret, None)
        else:
            return (ret, None)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()


class CommandLineParser:    
    def __init__(self):
        parser=argparse.ArgumentParser()
        parser.add_argument('--type', nargs=1, default=['avi'], type=str)
        parser.add_argument('--res', nargs=1, default=['720p'], type=str)
        parser.add_argument('--name', nargs=1, default=['selfCam'], type=str)

        self.args = parser.parse_args()


if __name__ == "__main__":
    opt = __import__('options')
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpu
    App(tk.Tk(), 'Video Recorder', opt)
