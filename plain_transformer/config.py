import torch

d_model = 512
n_heads = 8
n_layers = 4
d_k = 64
d_v = 64
d_ff = 2048
dropout = 0.1
padding_idx = 0
bos_idx = 2
eos_idx = 3
src_vocab_size = 32000
tgt_vocab_size = 32000
batch_size = 32
epoch_num = 40
early_stop = 5
lr = 3e-4

# greed decode的最大句子长度
max_len = 60
# beam size for bleu
beam_size = 3
# Label Smoothing
use_smoothing = False
# NoamOpt
use_noamopt = True

data_dir = './retained_data'
train_data_path = './retained_data/train'
dev_data_path = './retained_data/dev'
test_data_path = './retained_data/test'
model_path = 'D:/MSRA/project/transNMT_model/smoothing.pth'
log_path = './experiment/train.log'
output_path = './experiment/output.txt'

# gpu_id and device id is the relative id
# thus, if you wanna use os.environ['CUDA_VISIBLE_DEVICES'] = '2, 3'
# you should set CUDA_VISIBLE_DEVICES = 2 as main -> gpu_id = '0', device_id = [0, 1]
gpu_id = ''
device_id = [0, 1]

# set device
if gpu_id != '':
    device = torch.device(f"cuda:{gpu_id}")
else:
    device = torch.device('cpu')