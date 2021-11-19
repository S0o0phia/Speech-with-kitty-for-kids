import game_play
from tkinter import *
import tkinter.font as tkFont
from PIL import ImageTk, Image

def main():
    global my_canvas, bg
    bg = PhotoImage(file = './assets/main_merged.png')

    my_canvas = Canvas(root, width=1280, height=720)
    my_canvas.pack(fill = "both", expand = True)

    my_canvas.create_image(0,0, image = bg, anchor = "nw")

    fontStyle=tkFont.Font(family="카페24 써라운드", size=30)
    button1 = Button(my_canvas, width=7, height=2, text = "게임시작", background="#FFE8FF", font = fontStyle, command=next2)
    my_canvas.create_window(200, 550, anchor="nw", window=button1)
    
def next2():
    my_canvas.delete("all")
    bg2 = PhotoImage(file = './assets/next2.png')
    my_canvas.create_image(0,0, image = bg2, anchor = "nw")
    
    fontStyle=tkFont.Font(family="카페24 써라운드", size=20)
    
    button_set = []

    button_set.append(Button(root, width=5, height=1, text = "가-하", background="#FFE8FF", font = fontStyle, command=next3))
    button_set.append(Button(root, width=5, height=1, text = "고-호", background="#FFE8FF", font = fontStyle))
    button_set.append(Button(root, width=5, height=1, text = "그-흐", background="#FFE8FF", font = fontStyle))
    button_set.append(Button(root, width=5, height=1, text = "거-허", background="#FFE8FF", font = fontStyle))
    button_set.append(Button(root, width=5, height=1, text = "구-후", background="#FFE8FF", font = fontStyle))
    button_set.append(Button(root, width=5, height=1, text = "기-히", background="#FFE8FF", font = fontStyle))

    place_h = 250

    for button in button_set:
        my_canvas.create_window(350, place_h, anchor="nw", window=button)
        place_h += 70

    my_canvas.create_window(0, 0, anchor="nw", window=bg2)

def next3():
    my_canvas.delete("all")
    bg3 = PhotoImage(file = './assets/next3.png')
    my_canvas.create_image(0,0, image = bg3, anchor = "nw")
    fontStyle=tkFont.Font(family="카페24 써라운드", size=20)
    
    button8 = Button(root, width=6, height=1, text = "결과확인", background="#FFE8FF", font = fontStyle, command=next4)
    my_canvas.create_window(1125, 650, anchor="nw", window=button8)
    my_canvas.create_window(0, 0, anchor="nw", window=bg3)

def next4():
    my_canvas.delete("all")
    bg4 = PhotoImage(file = './assets/next4.png')
    my_canvas.create_image(0,0, image = bg4, anchor = "nw")
    my_canvas.create_window(0, 0, anchor="nw", window=bg4)

    btt = Image.open('./assets/button.png').resize((100, 50), Image.ANTIALIAS)
    btt = ImageTk.PhotoImage(btt)

def init():
    global root
    root = Tk()
    root.call('wm', 'iconphoto', root._w, PhotoImage(file='./assets/icon.png'))
    root.title("냥냥이와 말해요")
    root.geometry("1280x720")
    root.resizable(False, False)
    main()

if __name__ == '__main__':
    init()
    root.mainloop()