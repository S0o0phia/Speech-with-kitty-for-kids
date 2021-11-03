from genericpath import exists
import os
import cv2
import glob
import time
import face_alignment
from multiprocessing import Pool, Process, Queue

def run(gpu, files):
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu
    fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device='cuda')
    print('gpu={},n_files={}'.format(gpu, len(files)))
    tic = time.time()
    count = 0

    for (img_name, savename) in files:
        try:
            I = cv2.imread(img_name)
            points_list = fa.get_landmarks(I)

        except:     
            with open("./error_log.txt", '+a') as f:
                f.write(img_name)
                f.write('\n')
                continue
              
        with open(savename, 'w') as f:
            if(points_list is not None):
                for points in points_list:
                    for (x, y) in points:
                        f.write('({}, {})\t'.format(x, y))
                    f.write('\n')

        count += 1
        if(count % 1000 == 0):
            print('dst={},eta={}'.format(savename, (time.time()-tic)/(count) * (len(files) - count) / 3600.0))
        

if(__name__ == '__main__'):
    with open('imgs.txt', 'r') as f:
        folders = [line.strip() for line in f.readlines()]

    data = []

    for folder in folders:
        files = glob.glob(folder + "/*.jpg")
        for f in files:
            txt = f.replace('.jpg', '.txt')
            if os.path.exists(txt):
                continue
            data.append((f, txt))
        
    processes = []
    n_p = 3
    #gpus = ['0']
    bs = len(data) // n_p

    for i in range(n_p):
        if(i == n_p - 1):
            bs = len(data)
        p = Process(target=run, args=('0',data[:bs],))
        data = data[bs:]
        p.start()
        processes.append(p)

    assert(len(data) == 0)
    for p in processes:
        p.join()
