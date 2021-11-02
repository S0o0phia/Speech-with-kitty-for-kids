from multiprocessing.context import Process
import os
import glob
from moviepy.editor import VideoFileClip

path = "../GRID/"
origin = "../video_org"
file = "GRID_files.txt"

def get_duration(filename):
    clip = VideoFileClip(filename)
    return clip.duration

def run(origins, videos, dests):
    for i in range(0, len(videos)):
        j = 0

        rate = get_duration(origins[i])
        n = int(rate / 3)
        pc = rate % 3

        clips = []

        for j in range(0, n):
            base = j * 3
            cmd = "ffmpeg -ss {} -i {} -r 29.97 -to {} -vcodec copy -acodec copy -async 1 -strict -2 {}.mp4 -y".format(base, origins[i], 3, os.path.join(dests[i], str(j)))
            clips.append(os.path.join(dests[i], str(j)) + '.mp4')
            os.system(cmd)

        base = n * 3
        cmd = "ffmpeg -ss {} -i {} -r 29.97 -to {} -vcodec copy -acodec copy -async 1 -strict -2 {}.mp4 -y".format(base, origins[i], 3, os.path.join(dests[i], str(n)))
        clips.append(os.path.join(dests[i], str(n)) + '.mp4')
        os.system(cmd)

    with open(file, 'a') as f:
        for clip in clips:
            f.writeline(clip)

if(__name__ == '__main__'):
    files = glob.glob(origin + "/*.mp4")
    videos = [os.path.basename(file).replace(".mp4", "") for file in files]
    paths = [os.path.join(path, video + '/') for video in videos]
    
    for path in paths:
        if(not os.path.exists(path)):
            os.makedirs(path)

    processes = []
    n_p = 8

    for i in range(n_p):
        p = Process(target=run, args=(files, videos, paths))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()