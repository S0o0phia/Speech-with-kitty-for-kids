
import os
import glob
from shutil import copy

def make_txt(arr, type):
    for f in arr:
#    files = glob.glob(folder + "/*")
#    for f in files:
        lip = f.replace('../GRID_imgs/', '')
        lip = lip + '\n'

        with open(f'../data/swk_{type}.txt','+a') as t:
            t.write(lip)

with open('imgs.txt', 'r') as f:
    folders = [line.strip() for line in f.readlines()]

if __name__ == '__main__':
    pnt = len(folders) // 5
    train = folders[pnt:]
    val = folders[:pnt]
    make_txt(train, 'train')
    make_txt(val, 'val')


'''     
    if(not os.path.exists(wav)):
        os.remove(align)

with open('imgs.txt', 'r') as f:
    lines = f.readlines()
    with open('img_paths.txt', 'w') as d:
        for line in lines:
            line = line.replace('\n', '')
            d.write(line + '/\n')
'''