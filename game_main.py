from tkinter import *
from PIL import Image, ImageTk

class MainFrame(Frame):
    def __init__(self):
        super().__init__() 
#        self.wall = PhotoImage(file = "./assets/main.png")
        self.master.title("냥냥이와 말해요")
        self.pack(fill=BOTH, expand=1)

        self.place_window()

    def place_window(self):
        w = 1024
        h = 600

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        
        x = (sw - w) / 2
        y = (sh - h) / 2

        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

        wall = Image.open('./assets/main_merged.png').resize((w - 250, h - 200), Image.ANTIALIAS)
        wall = ImageTk.PhotoImage(wall)
        wall_label = Label(image = wall)
        wall_label.image = wall
        wall_label.place(x = x + 150, y = y - 100)


def main():
    root = Tk()
    root.call('wm', 'iconphoto', root._w, PhotoImage(file='./assets/icon.png'))

    main = MainFrame()
    root.mainloop()  

if __name__ == '__main__':
    main()  