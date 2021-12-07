import os
from tkinter.constants import ANCHOR
import cv2
import json
import videos
import requests
import argparse
import play_mov
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
        self.end = False
        self.delay = 1
        self.answer = []
        self.no_answer_lip = []
        self.no_answer_sound = []

        self.model = Predictor(opts)

        self.window = window
        self.window.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='./assets/icon.png'))
        self.video_source = video_source        
        self.window.title(window_title)
        self.fontStyle=tkFont.Font(family="카페24 써라운드", size=10)        

        self.timer=()
        self.vid = VideoCapture(self.video_source)
        self.audio_t = None

        rest_api_id = "ndx5kpranc"
        rest_api_pw = "aXGsfnDJOrp61883MiyBcpY1knb3E4tqPqB9G3mQ" 
        self.headers = {
            "Content-Type": "application/octet-stream",
            "X-NCP-APIGW-API-KEY-ID": rest_api_id,
            "X-NCP-APIGW-API-KEY": rest_api_pw,
        }
        self.stt_url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=Kor"

        self.canvas = tk.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack(fill = "both", expand = True)

        self.bg_image = tk.PhotoImage(file=r'D:\capstone\2021-1\project\Speech-with-kitty\assets\next3.png')
#        self.canvas.create_image(0, 0, image = self.bg, anchor = "nw")
        self.canvas.update()

        self.a_list = ['가방', '가위', '가지']
        self.img_list = []
        self.img_list.append(tk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\photos\가\size\가방.png"))
        self.img_list.append(tk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\photos\가\size\가위.png"))
        self.img_list.append(tk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\photos\가\size\가지.png"))

        self.count_quiz = 0
        self.len_quiz = len(self.img_list)
        self.suffle_quiz()
        self.update()
        #self.canvas.create_image(300, 310, image=ga_img1)
        #self.canvas.create_image(650, 310, image=ga_img2)
        #self.canvas.create_image(1000, 310, image=ga_img3)

        self.button_list = []
        btn_hint=tk.Button(self.window, text='힌트', background="#FFE8FF", font = self.fontStyle, command=self.play_mov)
        btn_hint.pack(side = tk.LEFT, fill="both", expand=True)
        btn_start=tk.Button(self.window, text='들어봐!', background="#FFE8FF", font = self.fontStyle, command=self.open_camera)
        btn_start.pack(side = tk.LEFT, fill="both", expand=True)
        btn_next=tk.Button(self.window, text='다른 문제', background="#FFE8FF", font = self.fontStyle, command=self.suffle_quiz)
        btn_next.pack(side = tk.LEFT, fill="both", expand=True)
        btn_submit = tk.Button(self.window, text = "결과확인", background="#FFE8FF", font = self.fontStyle, command=self.show_result)
        btn_submit.pack(side = tk.RIGHT, fill="both", expand=True)
        
        self.button_list.append(btn_hint)
        self.button_list.append(btn_start)
        self.button_list.append(btn_next)
        self.button_list.append(btn_submit)

        self.hearing = None
        self.thinking = None
        self.cat_says = None
        self.lip_image = None
        self.tmp_lip_image = None
        self.hearing_image = tk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\assets\ear.png")
        self.thinking_image = tk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\assets\loading.png")

        self.window.mainloop()

    def stt(self, value):
        with open('./output.wav', 'rb') as fp:
            audio = fp.read()

        try:
            res = requests.post(self.stt_url, headers=self.headers, data=audio)
            rescode = res.status_code
            if(rescode == 200):
                res_json = json.loads(res.text)
                value = res_json['text']

            else:
                print("Error : " + res.text)
        except Exception as e:
            print(e)
        
        return value

    def play_mov(self):
        print("play")
        play_mov.play_mov(str(self.count_quiz - 1))
        os.remove('audio.wav')

    def korean_to_be_englished(self, word):
        CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
        JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        
        r_lst = []
        
        for w in list(word.strip()):
            if '가' <= w <= '힣':
                ch1 = (ord(w) - ord('가')) // 588
                ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
                ch3 = (ord(w) - ord('가')) - (588 * ch1) - 28 * ch2
                r_lst.append([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
            else:   r_lst.append([w])
                
        return r_lst
        
    def startTimer(self):
        global count
        count += 1
        timer = threading.Timer(1, self.startTimer)
        timer.start()

        if count == 5:
            timer.cancel()
            self.close_camera()

    def audio_recording(self):
        fs = 16000
        record_voice = sounddevice.rec(int(5 * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write("output.wav", fs, record_voice)
        global count
        count = 0

    def open_camera(self):
        if self.a_list[self.count_quiz - 1] in self.answer:
            self.answer.remove(self.a_list[self.count_quiz - 1])
        elif self.a_list[self.count_quiz - 1] in self.no_answer_lip:
            self.no_answer_lip.remove(self.a_list[self.count_quiz - 1])
        elif self.a_list[self.count_quiz - 1] in self.no_answer_sound:
            self.no_answer_sound.remove(self.a_list[self.count_quiz - 1])

#        self.canvas.delete(self.lip_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image = self.bg_image, anchor = "nw")
        self.canvas.create_image(650, 310, image=self.img_list[self.count_quiz - 1])
        self.hearing = self.canvas.create_image(300, 500, image=self.hearing_image, anchor="nw")
#        self.cat_says = self.canvas.create_text(400, 600, text = "듣는중이냥!", font = self.fontStyle, fill = "white")

        self.ok = True
        print("camera opened => Recording Start ...")
        self.startTimer()
        self.audio_t = threading.Thread(target=self.audio_recording, args=())
        self.audio_t.start()

    def close_camera(self):
        self.audio_t.join()
        self.canvas.delete(self.hearing)
        self.thinking = self.canvas.create_image(300, 500, image=self.thinking_image, anchor="nw")
        self.ok = False
        print("camera closed => Recording Stopped")
        args = self.vid.args
        video, _ = videos.load_video('./' + args.name[0] + '.' + args.type[0])
        lip = self.model.predict(video)
        origin = self.a_list[self.count_quiz - 1]
        lip = self.a_list[self.count_quiz - 1]
        self.vid.out.release()
        os.remove('selfCam.avi')
        self.vid.out = cv2.VideoWriter(args.name[0] + '.' + args.type[0] , self.vid.fourcc , 29.97, self.vid.res)
        sound = self.stt("XP")

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image = self.bg_image, anchor = "nw")
        self.canvas.create_image(650, 310, image=self.img_list[self.count_quiz - 1])
        print('Done!')

        if lip == origin and sound == origin:
            self.canvas.delete(self.lip_image)
            self.cat_says = self.canvas.create_text(400, 600, text = "맞았냥~ 다음 문제로 넘어가라냥!", font = self.fontStyle, fill = "black")
            self.answer.append(origin)

        else:
            spl_ori = self.korean_to_be_englished(origin)
            spl_stt = self.korean_to_be_englished(sound)

            if len(spl_stt) > len(spl_ori):            
                self.canvas.delete(self.lip_image)
                self.cat_says = self.canvas.create_text(400, 600, text = "아웅~~ 조금만 짧게 말해줘라냥!", font = self.fontStyle, fill = "black")

            elif len(spl_stt) < len(spl_ori):            
                self.canvas.delete(self.lip_image)
                self.cat_says = self.canvas.create_text(400, 600, text = "조금만! 기일게 말해줘라냥!", font = self.fontStyle, fill = "black")

            else:
                diff_col = False

                for i in range(0, len(spl_stt)):
                    for j in range(0, len(spl_stt[i])):
                        if (spl_stt[i][j] != spl_ori[i][j]) and (j % 2 == 1):
                            diff_col = True

                if diff_col:
                    self.cat_says = self.canvas.create_text(315, 500, text = "'{}'이라고 말했냥~\n입모양에 문제가 있는 것 같다 냥! 입을 이렇게 해보면 어때 냥?".format(sound), font = self.fontStyle, fill = "black", anchor="nw")
                    self.tmp_lip_image = PIL.ImageTk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\photos\lips\a.gif")
                    self.lip_image = self.canvas.create_image(315, 560, image=self.tmp_lip_image, anchor="nw")
                    self.no_answer_lip.append(origin)
                    
                else:
                    self.cat_says = self.canvas.create_text(315, 520, text = "'{}'이라고 말했냥~\n혀 위치에 문제가 있는 것 같다 냥! 혀를 이 위치에 대야 해 냥!".format(sound), font = self.fontStyle, fill = "black", anchor="nw")
                    self.tmp_lip_image = PIL.ImageTk.PhotoImage(file=r"D:\capstone\2021-1\project\Speech-with-kitty\photos\tough\a.gif")
                    self.lip_image = self.canvas.create_image(315, 560, image=self.tmp_lip_image, anchor="nw")
                    self.no_answer_sound.append(origin)
                    

    def suffle_quiz(self):
        print("Suffle!")

        if self.count_quiz == self.len_quiz:
            self.show_result()
        else:
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image = self.bg_image, anchor = "nw")
            self.canvas.create_image(650, 310, image=self.img_list[self.count_quiz])
            self.cat_says = self.canvas.create_text(400, 600, text = "화이팅하라냥~", font = self.fontStyle, fill = "black")
            self.count_quiz += 1

    def show_result(self):
        self.end = True
        self.canvas.delete(self.cat_says)

        for btn in self.button_list:
            btn.pack_forget()
#        self.canvas.delete("all")

        self.bg_image = tk.PhotoImage(file = r'D:\capstone\2021-1\project\Speech-with-kitty\assets\next4.png')
        self.canvas.create_image(0, 0, image = self.bg_image, anchor = "nw")

        answers = ""
        no_answers = ""

        for a in self.answer:
            answers += a + "\n"

        for a in self.no_answer_lip:
            no_answers += a + "\n"

        for a in self.no_answer_sound:
            no_answers += a + "\n"

        self.canvas.create_text(235, 215, text = answers, font = self.fontStyle, fill = "black")
        self.canvas.create_text(825, 215, text = no_answers, font = self.fontStyle, fill = "black")

        if len(self.no_answer_lip) > len(self.no_answer_sound):
            self.cat_says = self.canvas.create_text(400, 600, text = "수고했다 냥~ 입모양만 조금 더 연습하자 냥!", font = self.fontStyle, fill = "black")
        elif len(self.no_answer_lip) < len(self.no_answer_sound):
            self.cat_says = self.canvas.create_text(400, 600, text = "수고했다 냥~ 혀 위치에 조금 더 신경쓰자 냥!", font = self.fontStyle, fill = "black")
        elif len(self.no_answer_lip) == 0:
            self.cat_says = self.canvas.create_text(400, 600, text = "수고했다 냥! 오늘 너무 완벽했다 냥~", font = self.fontStyle, fill = "black")
        else:
            self.cat_says = self.canvas.create_text(400, 600, text = "수고했다 냥~ 틀린 단어는 입 모양이랑 혀 위치를 더 연습하자 냥~", font = self.fontStyle, fill = "black")

    def update(self):
        ret, frame = self.vid.get_frame()
        frame_show = frame

        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        if ret and not self.end:
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

        self.res = STD_DIMENSIONS[self.args.res[0]]
        print(self.args.name, self.fourcc, self.res)
        self.out = cv2.VideoWriter(self.args.name[0] + '.' + self.args.type[0] , self.fourcc , 29.97, self.res)

        self.vid.set(3, self.res[0])
        self.vid.set(4, self.res[1])
        self.width, self.height=self.res

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret: return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:   return (ret, None)
        else:
            return (None, None)

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

def play_game():
    global root
    root.destroy()

    opt = __import__('options')
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpu
    App(tk.Tk(), '냥냥이랑 놀자!', opt)

def main():
    global root
    global my_canvas
    bg = tk.PhotoImage(file = r'D:\capstone\2021-1\project\Speech-with-kitty\assets\main_merged.png')

    my_canvas = tk.Canvas(root, width=1280, height=720)
    my_canvas.pack(fill = "both", expand = True)

    my_canvas.create_image(0,0, image = bg, anchor = "nw")
    fontStyle=tkFont.Font(family="카페24 써라운드", size=30)
    button1 = tk.Button(my_canvas, width=7, height=2, text = "게임시작", background="#FFE8FF", font = fontStyle, command=play_game)
    my_canvas.create_window(200, 550, anchor="nw", window=button1)

    root.mainloop()

if __name__ == "__main__":
    global root
    root = tk.Tk()
    root.title("냥냥이와 말해요")
    root.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='./assets/icon.png'))
    root.geometry("1280x720")
    root.resizable(False, False)

    main()
