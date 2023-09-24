import sys
# sys.path.append('../input/pytorch-image-models/pytorch-image-mopdels-master')

from tqdm import tqdm
import random
import os
import pandas as pd
import numpy as np

# Visuals and CV2
import matplotlib.pyplot as plt
import cv2

# albumentations for augs
import albumentations
from albumentations.pytorch.transforms import ToTensorV2

# torch
import torch
import timm
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts, CosineAnnealingLR, ReduceLROnPlateau

import warnings
warnings.filterwarnings('ignore')

# Configuration
DIM = (512, 512)

NUM_WORKERS = 4
BATCH_SIZE = 16
EPOCHS = 1
SEED = 2020
LR = 3e-4

TRAIN_IMG = '/Users/payap/tensorflow_datasets/siamese/1_shopee/train_images'

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

MODEL_NAME = 'efficientnet_b0'

SCHEDULER = 'CosineAnnealingWarmRestarts'
T_0 = 3
min_lr = 1e-6

# Utils
def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    torch.cuda.manual_seed(seed)

seed_everything(SEED)

class AverageMeter(object):
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
        
    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
        
# Augs
def get_train_transforms():
    return albumentations.Compose(
        [
            albumentations.HorizontalFlip(p=0.5),
            albumentations.VerticalFlip(p=0.5),
            albumentations.Rotate(limit=120, p=0.8),
            albumentations.RandomBrightness(limit=(0.09, 0.6), p=0.5),
            # albumentations.Cutout(num_holes=8, max_h_size=8, max_w_size=8, fill_value=0, always_apply=False, p=0.5),
            # albumentations.ShiftScaleRotate(shift_limit=0.25, scale_limit=0.1, rotate_limit=0),
            albumentations.Normalize(
                MEAN, STD, max_pixel_value=255.0, always_apply=True
            ),
            
            ToTensorV2(p=1.0)
        ]
    )
    
def get_valid_transforms():
    return albumentations.Compose((
        [
            albumentations.Normalize(MEAN, STD, max_pixel_value=255.0, always_apply=True),
            ToTensorV2(p=1.0)
        ]
    ))    
    
# Dataset
class SiameseNetworkDataset(Dataset):
    def __init__(self, image_1, image_2, title_1, title_2, labels, dim=(512, 512), augmentation=None):
        self.image_1 = image_1
        self.image_2 = image_2
        self.title_1 = title_1
        self.title_2 = title_2
        self.labels = labels
        self.dim = dim
        self.augmentation = augmentation
        
    def __len__(self):
        return len(self.image_1)
    
    def __getitem__(self, index):
        img_0 = self.image_1[index]
        img_1 = self.image_2[index]
        
        img_0_path = os.path.join(TRAIN_IMG, img_0)
        img_1_path = os.path.join(TRAIN_IMG, img_1)
        
        if not os.path.exists(img_0_path) or not os.path.exists(img_1_path):
            # Skip this iteration if either image file doesn't exist
            print("there is no image")
            return self.__getitem__((index + 1) % len(self.image_1))
        
        img_0 = cv2.imread(img_0_path)
        img_1 = cv2.imread(img_1_path)
        
        img_0 = cv2.cvtColor(img_0, cv2.COLOR_BGR2RGB)
        img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)
        
        title_1 = self.title_1[index]
        title_2 = self.title_2[index]
        
        if self.dim:
            img_0 = cv2.resize(img_0, self.dim)
            img_1 = cv2.resize(img_1, self.dim)
            
        if self.augmentation:
            augmented_0 = self.augmentation(image=img_0)
            augmented_1 = self.augmentation(image=img_1)
            img_0 = augmented_0['image']
            img_1 = augmented_1['image']
            
        return img_0, img_1, title_1, title_2, torch.tensor(self.labels[index], dtype=torch.float32)
    
# Model
class SiameseModel(nn.Module):
    def __init__(self, model_name='efficientnet_b0', out_features=2, pretrained=True):
        super().__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained)
        n_features = self.model.classifier.in_features
        
        self.model.global_pool = nn.Identity()
        self.model.classifier = nn.Identity()
        self.pooling = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Linear(n_features, n_features//2),
            nn.ReLU(),
            nn.Linear(n_features//2, out_features)
        )
        
    def forward_once(self, x):
        bs = x.size(0)
        output = self.model(x)
        output = self.pooling(output).view(bs, -1)
        
        output = self.classifier(output)
        
        return output
    
    def forward(self, image_1, image_2):
        output1 = self.forward_once(image_1)
        output2 = self.forward_once(image_2)
        return output1, output2
    
d = SiameseModel(model_name='efficientnet_b0', pretrained=True)
t1 = torch.ones((1, 3, 512, 512))
t2 = torch.ones((1, 3, 512, 512))
x1, x2 = d(t1, t2)

print(x1.size())
print(x2.size())

del x1, x2, t1, t2, d

# torch.Size([1, 2])
# torch.Szie([1, 2])

# Loss
class ContrastiveLoss(torch.nn.Module):
    # Based on: http://tann.lecun.com/exdb/publis/pdf/hadse11-chopra-lecun-06.pdf
    def __init__(self, margin=2.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
        
    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2)
        loss_contrastive = torch.mean((1 - label) * torch.pow(euclidean_distance, 2) + (label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))
        
        return loss_contrastive
    
# Train-Loop
def train_fn(dataloader, model, criterion, optimizer, device, scheduler, epoch):
    model.train()
    loss_score = AverageMeter()
    
    tk0 = tqdm(dataloader, total=len(dataloader))
    for img_0, img_1, title_1, title_2, label in tk0:
        img_0 = img_0.to(device)
        img_1 = img_1.to(device)
        
        label = label.to(device)
        
        batch_size = img_0.shape[0]
        
        optimizer.zero_grad()
        
        output_1, output_2 = model(img_0, img_1)
        
        loss = criterion(output_1, output_2, label)
        loss.backward()
        optimizer.step()
        
        loss_score.update(loss.detach().item(), batch_size)
        
        tk0.set_postfix(Train_Loss=loss_score.avg, Epoch=epoch, LR=optimizer.param_groups[0]['lr'])
        
    if scheduler is not None:
        scheduler.step()
        
    return loss_score

# Engine
def run():
    df = pd.read_csv('/Users/payap/tensorflow_datasets/siamese/1_shopee/siamese_data.csv')
    
    # Defining DataSet
    train_dataset = SiameseNetworkDataset(
        image_1=df['image_1'].values.tolist(),
        image_2=df['image_2'].values.tolist(),
        title_1=df['title_1'].values.tolist(),
        title_2=df['title_2'].values.tolist(),
        labels=df['label'].values.tolist(),
        dim = DIM,
        augmentation=get_train_transforms(),
    ) 
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        pin_memory=True,
        drop_last=False,
        num_workers=NUM_WORKERS
    )

    
    # Defining Device
    device = torch.device("cpu")
    
    # Defining Model for specific fold
    model = SiameseModel(model_name= MODEL_NAME,out_features=64,pretrained=True)
    model.to(device)
    
    #DEfining criterion
    criterion = ContrastiveLoss()
    criterion.to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    # Defining LR scheduler
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=T_0)
    
    # The Engine Loop
    best_loss = 10000
    for epoch in range(EPOCHS):
        train_loss = train_fn(train_loader, model, criterion, optimizer, device,scheduler=scheduler, epoch=epoch)
        
        if train_loss.avg < best_loss:
            best_loss = train_loss.avg
            torch.save(model.state_dict(), f'model_best_loss.bin')
            
    torch.save(model.state_dict(), "siamesee_shopee.h5")
            
if __name__ == '__main__':
    run()
                

