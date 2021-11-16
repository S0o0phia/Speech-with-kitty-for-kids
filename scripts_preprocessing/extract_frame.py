import os
import time
from scipy.misc import imsave
from multiprocessing import Pool
from torch.utils.data import DataLoader, Dataset

class MyDataset(Dataset):
    def __init__(self):
        self.IN = '../GRID/'
        self.OUT = '../GRID_imgs/'
        self.wav = '../GRID_wavs/'
        self.path_video = 'GRID_files.txt'
        self.path_write = 'imgs.txt'

        with open(self.path_video, 'r') as f:
            files = [line.strip() for line in f.readlines()]

        self.files = []
        try:
            for file in files:  
                if(not os.path.exists(file)): continue
                _, ext = os.path.splitext(file)
                if(ext == '.XML'): continue
                self.files.append(file)
                wav = file.replace(self.IN, self.wav).replace(ext, '.wav')
                path = os.path.split(wav)[0]
                if(not os.path.exists(path)): 
                    os.makedirs(path)
        except:
            pass

    def __len__(self):
        return len(self.files)
        
    def __getitem__(self, idx):
        file = self.files[idx]
        _, ext = os.path.splitext(file)
        dst = file.replace(self.IN, self.OUT).replace(ext, '')

        if(not os.path.exists(dst)): 
            os.makedirs(dst)
        
        with open(self.path_write, 'a+') as f:
            cmd = 'ffmpeg -i "{}" -qscale:v 2 -r 29.97 "{}/%d.jpg"'.format(file, dst)
            f.write(dst + '\n')
            os.system(cmd)

            wav = file.replace(self.IN, self.wav).replace(ext, '.wav')    
            cmd = 'ffmpeg -y -i "{}" -async 1 -ac 1 -vn -acodec pcm_s16le -ar 16000 "{}" '.format(file, wav)
            os.system(cmd)

        return dst

if(__name__ == '__main__'):   
    dataset = MyDataset()
    loader = DataLoader(dataset, num_workers=0, batch_size=128, shuffle=False, drop_last=False)
    tic = time.time()
    for (i, batch) in enumerate(loader):
        eta = (1.0 * time.time() - tic) / (i + 1) * (len(loader) - i)
        print('eta: {}'.format(eta / 3600.0))