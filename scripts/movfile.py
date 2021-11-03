'''
import os
import glob
from shutil import copy

with open('imgs.txt', 'r') as f:
    folders = [line.strip() for line in f.readlines()]

data = []

for folder in folders:
    files = glob.glob(folder + "/*.txt")
    for f in files:
        txt = f.replace('GRID_imgs/', 'GRID/landmarks/')
        path, _ = os.path.split(txt)
        if(not os.path.exists(path)):
            os.makedirs(path)
        copy(f, txt)
'''

with open('imgs.txt', 'r') as f:
    lines = f.readlines()
    with open('img_paths.txt', 'w') as d:
        for line in lines:
            line = line.replace('\n', '')
            d.write(line + '/\n')