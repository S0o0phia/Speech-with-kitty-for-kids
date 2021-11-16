from model import LipNet
from dataset import MyDataset

import torch
import torch.nn as nn

class Predictor():
    def __init__(self, opt):
        self.opt = opt
        self.model = LipNet()
        self.model = self.model.cuda()
        self.net = nn.DataParallel(self.model).cuda()
        self.set_model()
    
    def set_model(self):
        if(hasattr(self.opt, 'weights')):
            pretrained_dict = torch.load(self.opt.weights)
            model_dict = self.model.state_dict()
            pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict.keys() and v.size() == model_dict[k].size()}
            missed_params = [k for k, v in model_dict.items() if not k in pretrained_dict.keys()]
            print('loaded params/tot params:{}/{}'.format(len(pretrained_dict),len(model_dict)))
            print('miss matched params:{}'.format(missed_params))
            model_dict.update(pretrained_dict)
            self.model.load_state_dict(model_dict)
        else:
            print("Model not available! Default weight is loading ...")

    def ctc_decode(self, y):
        y = y.argmax(-1)
        t = y.size(0)
        result = []

        for i in range(t + 1):
            result.append(MyDataset.ctc_arr2txt(y[:i], start=1))
            
        return result

    def predict(self, video):
        y = self.model(video[None,...].cuda())
        txt = self.ctc_decode(y[0])
        return(txt[-1])
