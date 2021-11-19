import os
import cv2
import json
import videos
import requests
import argparse
import threading
import sounddevice
import tkinter as tk
import tkinter.font as tkFont
import PIL.Image, PIL.ImageTk
from predictor import Predictor
from scipy.io.wavfile import write

count = 0
answer = [] # 정답
non_answer = [] # 오답

class App:
    def __init__(self, window, window_title, opts, video_source=0):
        self.ok = False
        self.delay = 10
        self.window = window
        self.suffle_problem()
        self.model = Predictor(opts)
        self.video_source = video_source        
        self.window.title(window_title)
        fontStyle=tkFont.Font(family="카페24 써라운드", size=10)        

        ear = cv2.imread('assets/ear.png', cv2.IMREAD_COLOR)
        ear = cv2.resize(ear, (300, 300), interpolation = cv2.INTER_CUBIC)
        mask = cv2.cvtColor(ear, cv2.COLOR_BGR2GRAY)
        mask[mask[:] == 255] = -1
        mask[mask[:] >= 0] = 255
        mask[mask[:] == -1] = 0
        self.mask_inv = cv2.bitwise_not(mask)
        self.ear = cv2.bitwise_and(ear, ear, mask=mask)

        self.timer=()
        self.vid = VideoCapture(self.video_source)
        self.audio_t = threading.Thread(target=self.audio_recording, args=())

        self.stt_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
        self.rest_api_key = '989e297c8f98f0f1b207ff218bc42740'
        self.stt_headers = {
            "Content-Type": "application/octet-stream",
            "X-DSS-Service": "DICTATION",
            "Authorization": "KakaoAK " + self.rest_api_key,
        }

        self.bg = tk.PhotoImage(file=r'C:\Users\chw06\OneDrive\capstone\2021-1\project\Speech-with-kitty-for-kids\assets\next3.png')
        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack(fill = "both", expand = True)

        self.canvas.create_image(0, 0, image = self.bg, anchor = "nw")
#        self.canvas.create_window(0, 0, window = self.bg, anchor = "nw")
        self.canvas.update()

        btn_start=tk.Button(window, text='들어봐!', background="#FFE8FF", font = fontStyle, command=self.open_camera)
        btn_start.pack(side = tk.LEFT)
        
        btn_next=tk.Button(window, text='다른 문제', background="#FFE8FF", font = fontStyle, command=self.suffle_problem)
        btn_next.pack(side = tk.LEFT)
                
        btn_submit = tk.Button(window, text = "결과확인", background="#FFE8FF", font = fontStyle, command=None)
        btn_submit.pack(side = tk.RIGHT)

        self.update()
        self.window.mainloop()

    def stt(self):
        with open('output.wav', 'rb') as fp:
            audio = fp.read()

        try:
            res = requests.post(self.stt_url, headers=self.headers, data=audio)
            #print(res.text)
            result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}') + 1]
            result = json.loads(result_json_string)
            value = result['value']
            print(result['value'])
        except:
            print("XP")
            
        
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
#        print(args.name[0] + '.' + args.type[0])
        video, _ = videos.load_video('./' + args.name[0] + '.' + args.type[0])
        lip = self.model.predict(video)
        sound = self.stt()
        print(lip, sound)


    def suffle_problem(self):
        pass

    def update(self):
        ret, frame = self.vid.get_frame()
        frame_show = frame

        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            h, w, c = self.ear.shape
            fh = 720 - h
            roi = frame_show[fh : fh + h, 0 : w]
            back = cv2.bitwise_and(roi, roi, mask=self.mask_inv)
            dst = cv2.add(self.ear, back)
            frame_show[fh : fh + h, 0 : w] = dst

        if ret:
            frame_show = cv2.resize(frame_show, (340, 180))
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_show))
            self.canvas.create_image(850, 500, image = self.photo, anchor = tk.NW)

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
        self.width, self.height=res

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

def main():
    opt = __import__('options')
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpu
    App(tk.Tk(), '냥냥이랑 놀자!', opt)

if __name__ == "__main__":
    main()
