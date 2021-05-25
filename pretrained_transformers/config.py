import torch

data_dir = '../retained_data'
train_data_path = '../retained_data/train'
dev_data_path = '../retained_data/dev'
test_data_path = '../retained_data/test'
model_dir = 'D:/MSRA/project/transformers_model/best/'


# gpu_id and device id is the relative id
# thus, if you wanna use os.environ['CUDA_VISIBLE_DEVICES'] = '2, 3'
# you should set CUDA_VISIBLE_DEVICES = 2 as main -> gpu_id = '0', device_id = [0, 1]
gpu_id = '0'
device_id = [0, 1]

# set device
if gpu_id != '':
    device = torch.device(f"cuda:{gpu_id}")
else:
    device = torch.device('cpu')