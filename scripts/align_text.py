#음성인식
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

#파일 자르기
np.set_printoptions(precision=6, suppress=True)

wav = './cut.wav'
(file_dir, file_id) = os.path.split(wav)
print("file_dir:", file_dir)
print("file_id:", file_id)

# original
y, sr = librosa.load(wav, sr=16000)
time = np.linspace(0, len(y), len(y)) # time axis
fig, ax1 = plt.subplots() # plot
ax1.plot(time, y, color = 'b', label='speech waveform')
ax1.set_ylabel("Amplitude") # y 축
ax1.set_xlabel("Time [s]") # x 축
plt.title(file_id) # 제목
plt.savefig(file_id+'.png')
#plt.show()
#librosa.output.write_wav('original_file.mp3', y, sr) # original wav to save mp3 file

#y.tolist()

def findzero(arr,i):
    while i < len(arr):
        a = len(arr) - i
        if a < 1000:
            return -1
        if arr[i] == 0.0:           
            return i
        else:
            i += 1

def nozero(arr,i):
    while i < len(arr):
        a = len(arr) - i
        if a < 1000:
            return -1
        if  arr[i] < 0.04 and arr[i]> -0.04:
            #print('+1')
            i+=1
        else:
            #print('찾았다')
            return i

def main(arr):
    i = 0
    num = 0
    ij_list = []
    while i < len(arr):
        i = nozero(arr,i)
        if i == -1:
            break
        j = findzero(arr,i)
        if j == -1:
            break
        #print('저장 인덱스', i, j)
        ij_list.append([i,j])
        sf.write('./save/cut_file{}.wav'.format(num), arr[i:j], sr)
        num += 1
        i = j
    ij_list = np.array(ij_list)
    print(ij_list)
    return num, ij_list

#cut 실행
num, ij_list = main(y)

#묵음붙이기
i = 0
while i < num:
    #print("확인")
    audio_in_file = "./save/cut_file{}.wav".format(i)
    audio_out_file = "./save/add/add_cut_file{}.wav".format(i)

    one_sec_segment = AudioSegment.silent(duration=1000)

    song = AudioSegment.from_wav(audio_in_file)   
    final_song = one_sec_segment + song
    final_song.export(audio_out_file, format="wav")
    i+=1

# 카카오 음성인식
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
    with open("./save/add/add_cut_file{}.wav".format(i), 'rb') as fp:
        audio = fp.read()

    res = requests.post(kakao_speech_url, headers=headers, data=audio)

    #print(res.text)
    try:
        result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
        result = json.loads(result_json_string)
        #print(result)
        value = result['value']
        value_list.append(value)
        print(result['value'])
    except:
        value_list.append('sp')
        pass
    i+=1

i = 0
f = open('./result.align', 'a', encoding='utf-8')
str_line = '0 ' + str(ij_list[0][0]-1) + ' sil\n'
f.write(str_line)
while i < num:
    str_line = str(ij_list[i][0]) + ' ' + str(ij_list[i][1]) + ' ' +str(value_list[i]) + '\n'
    f.write(str_line)
    i += 1
str_line = str(ij_list[i-1][1]+1) + ' ' + str(len(y)) + ' sil\n'
f.write(str_line)
f.close()