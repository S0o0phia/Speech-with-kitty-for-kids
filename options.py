gpu = '0'               # 훈련 및 테스트에 사용되는 GPU ID
random_seed = 0	        # 훈련 및 테스트를 위한 무작위 시드
data_type = 'unseen'	# GRID Corpus에서 데이터 분할, `unseen` 및 `overlap`이 지원됩니다.
vid_padding = 75        # 비디오 패딩 길이, 각 비디오는 0만큼 `vid_padding`으로 패딩됩니다.
txt_padding = 20       # txt 패딩 길이, 각 txt는 0만큼 `txt_padding`으로 채워집니다.
batch_size = 1         # 훈련 및 테스트를 위한 배치 크기
num_workers = 0        # 데이터 로딩에 사용된 프로세스 수
max_epoch = 5000       # 훈련을 위한 최대 epoch
display = 10           # 훈련 및 테스트의 표시 간격입니다. 예를 들어 `display=10`이면 프로그램은 10번의 반복 후에 한 번만 인쇄됩니다.
test_step = 500        # 테스트 및 스냅샷 간격입니다. 예를 들어 `test_step=1000`이면 프로그램은 1000번의 훈련 반복 후에 테스트합니다.
save_prefix = './weights/swk_trained/'     # 모델 체크포인트의 저장 접두사.
is_optimize = True  # 훈련 모드입니다. 'False'로 설정하면 모델이 한 번 테스트하고 종료됩니다.
val_list = './data/swk_val.txt'
train_list = './data/swk_train.txt'	# 훈련 색인 파일. 각 줄에는 `s5/video/mpg_6000/lgbs5a`와 같은 비디오 폴더가 있습니다. `dataset.py`는 프레임 순서에 따라 폴더의 모든 `*.jpg` 파일을 읽습니다. (테스트 인덱스 파일 = `train_list`와 동일)
anno_path = './GRID/align/'                # 각 동영상에 대한 주석 파일 `*.align`을 포함하는 주석 루트.
video_path = './GRID/lip/'
base_lr = 2e-5      # 학습률

#사전 훈련된 가중치의 위치입니다. 모델은 훈련 또는 테스트 전에 이 가중치를 로드합니다. 이 매개변수가 누락되면 모델이 처음부터 학습됩니다.
weights = './weights/swk_trained/_loss_0.09086905419826508_wer_0.0_cer_0.0.pt'
