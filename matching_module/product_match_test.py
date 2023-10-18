import torch
import pandas as pd
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
from siamese_shopee_train import SiameseModel, SiameseNetworkDataset, get_valid_transforms

DIM = (512, 512)

NUM_WORKERS = 4
BATCH_SIZE = 16

# 모델 가중치 파일 경로
model_weights_path = "model_best_loss.bin"

# 테스트 데이터셋을 로드
df = pd.read_csv('/Users/payap/tensorflow_datasets/siamese/1_shopee/siamese_data.csv')
test_dataset = SiameseNetworkDataset(
        image_1=df['image_1'].values.tolist(),
        image_2=df['image_2'].values.tolist(),
        title_1=df['title_1'].values.tolist(),
        title_2=df['title_2'].values.tolist(),
        labels=df['label'].values.tolist(),
        dim = DIM,
        augmentation=get_valid_transforms(),
    )

# DataLoader 설정
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 모델 초기화 및 가중치 로드
model = SiameseModel(model_name='efficientnet_b0', out_features=64, pretrained=False)  # 모델 초기화
model.load_state_dict(torch.load(model_weights_path))
model.eval()  # 평가 모드로 설정

# Lists to store true labels and predicted labels
true_labels = []
predicted_labels = []

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Iterate through the test data
for img_0, img_1, title_1, title_2, label in test_loader:
    img_0 = img_0.to(device)
    img_1 = img_1.to(device)
    label = label.to(device)

    # Forward pass
    with torch.no_grad():
        output_1, output_2 = model(img_0, img_1)

    # Calculate predicted labels
    predicted_labels.extend((output_1 - output_2).cpu().numpy())
    true_labels.extend(label.cpu().numpy())

# Convert predicted labels to binary (0 or 1) based on a threshold
threshold = 0.5
predicted_labels = [1 if pred > threshold else 0 for pred in predicted_labels]

# Calculate accuracy
accuracy = accuracy_score(true_labels, predicted_labels)

print(f"Accuracy: {accuracy}")
