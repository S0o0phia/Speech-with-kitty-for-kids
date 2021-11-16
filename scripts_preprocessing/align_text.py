#음성인식
from operator import add
from librosa.effects import trim
from numpy.lib.shape_base import expand_dims
import requests
import json

#음성파일 자르기
import librosa
import soundfile as sf
import os
import numpy as np
import matplotlib.pyplot as plt

#묵음 붙이기
from pydub import AudioSegment
from pydub.playback import play

#glob
from glob import glob
import os

#파일 자르기
np.set_printoptions(precision=6, suppress=True)

from pydub import AudioSegment
from pydub.playback import play

def speed_change(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

#golb 함수
def get_addresses():
    with open("./imgs.txt",'r') as f:
        addresses = f.readlines()
    arr_list = []
    for address in addresses:
        address = address.replace('\n', '')
        address = address.replace('/GRID_imgs', '/GRID_wavs')
        arr_list.append(address)
    return arr_list
'''
def findzero(arr,i):
    while i < len(arr):
        a = len(arr) - i
        if a < 1000:    return -1
        if arr[i] == 0.0:   return i
        i += 1

def nozero(arr, i):
    loud = max(arr)
    sil = loud * 0.03
    cnt = 0
    while i < len(arr):
        if arr[i] < sil and arr[i]> -(sil):
            cnt += 1
            i += 1
        elif cnt > 1000:
            return i
        else:
            cnt = 0
            i += 1
    return -1
'''
def get_index(arr, split):
    '''
    i = 0
    num = 0
    ij_list = []
    while i < len(arr):
        i = nozero(arr,i)
        if i == -1: break
        j = findzero(arr,i)
        if j == -1: break
        #print('저장 인덱스', i, j)
        ij_list.append([i,j])
        sf.write(f'../GRID/wavs/cut_file{num}.wav', arr[i - 1000 : j + 1000], sr)
        num += 1
        i = j
    '''
    num = 0
    ij_list = []
    for s in split:
        i = s[0]
        j = s[1]
        sf.write('../GRID/wavs/cut_file{}.wav'.format(num), arr[i : j], sr)
        ij_list.append([i,j])
        num += 1

    ij_list = np.array(ij_list)
    return num, ij_list

if(__name__ == '__main__'):
    addresses = get_addresses()
    for address in addresses:
        wav_origin = address + '.wav'
        wav = address + '_noise.wav'
        (file_dir, file_id) = os.path.split(wav)
        print("file_dir:", file_dir)
        print("file_id:", file_id)
        '''
        # decrease noise
        cmd = f'sox {wav_origin} -n noiseprof noise.prof'   
        os.system(cmd)
        cmd = f'sox {wav_origin} {wav} noisered noise.prof 0.001'
        os.system(cmd)
        '''
        # original file load, cut 실행
        y, sr = librosa.load(wav, sr=16000)
        sp = librosa.effects.split(y=y, frame_length=16000, top_db=0.5)

        print(sp)
        num, ij_list = get_index(y, sp)

        #time = np.linspace(0, len(y), len(y)) # time axis
        #fig, ax1 = plt.subplots() # plot
        #ax1.plot(time, y, color = 'b', label='speech waveform')
        #ax1.set_ylabel("Amplitude") # y 축
        #ax1.set_xlabel("Time [s]") # x 축
        #plt.title(file_id) # 제목
        #plt.savefig(file_id+'.png')
        #plt.show()

        #묵음붙이기
        i = 0
        audio_in_file = '../GRID/wavs/cut_file{}.wav'

        while i < num:
            #print("확인")
#            audio_out_file = "./save/add/add_cut_file{}.wav".format(i)
            one_sec_segment = AudioSegment.silent(duration=1000, frame_rate=16000)
            song = AudioSegment.from_wav(audio_in_file.format(i))   
            song += 30
            final_song = one_sec_segment + song + one_sec_segment
            final_song.export(audio_in_file, format="wav")
            i += 1

        i = 0
        value_list = []
        while i < num:
            kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
            rest_api_key = '989e297c8f98f0f1b207ff218bc42740'
            headers = {
                "Content-Type": "application/octet-stream",
                "X-DSS-Service": "DICTATION",
                "Authorization": "KakaoAK " + rest_api_key,
            }
            with open(audio_in_file.format(i), 'rb') as fp:
                audio = fp.read()

            try:
                res = requests.post(kakao_speech_url, headers=headers, data=audio)
                #print(res.text)
                result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
                result = json.loads(result_json_string)
                #print(result)
                value = result['value']
                value_list.append(value)
                print(result['value'])
            except:
                value_list.append('SP')
            
            i+=1

        dst = address.replace('.wav', '')
        dst = address.replace('/GRID_wavs', '/GRID/align')
        path, name = os.path.split(dst)
        if(not os.path.exists(path)):
            os.makedirs(path)
        dst = dst + '.align'
        f = open(dst, 'w', encoding='utf-8')
        if len(ij_list) == 0:
            continue
        elif(ij_list[0][0] != 0):
            str_line = '0 ' + str(ij_list[0][0]-1) + ' SIL\n'
            f.write(str_line) 
            
        i = 0
        while i < num:
            str_line = str(ij_list[i][0]) + ' ' + str(ij_list[i][1]) + ' ' +str(value_list[i]) + '\n'
            f.write(str_line)
            i += 1

        str_line = str(ij_list[i-1][1]+1) + ' ' + str(len(y)) + ' SIL\n'
        f.write(str_line)
        f.close()