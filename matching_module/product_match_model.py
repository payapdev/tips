import torch
import pandas as pd
import numpy as np
import cv2
import requests
import json
from PIL import Image
from io import BytesIO
from torchvision import transforms
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score
from siamese_shopee_train import SiameseModel, SiameseNetworkDataset, get_valid_transforms
from tqdm import tqdm

# declair
crawled_dataset = []

# csv 파일 경로
project_path = '/Users/payap/development/tips/'
csv_file_path = project_path + 'data/'
comparison_file_name = 'tips_data.csv'
validation_file_name = 'crawled_data.csv'

comparison_file_path = csv_file_path + comparison_file_name
validation_file_path = csv_file_path + validation_file_name

# csv 파일 불러오기
comparison_data = pd.read_csv(comparison_file_path)
comp_keywords = comparison_data['search_word'].values.tolist()
comp_ver = comparison_data['ver'].str.split('.').tolist()
comp_opt = [comparison_data['option 1'].str.split('.').tolist(), comparison_data['option 2'].str.split('.').tolist()]

val_df = pd.read_csv(validation_file_path)
keywords = val_df['keyword'].values.tolist()
tikis = val_df['tiki'].values.tolist()
lazadas = val_df['lazada'].values.tolist()

DIM = (512, 512)

NUM_WORKERS = 4
BATCH_SIZE = 16

# 모델 가중치 파일 경로
model_weights_path = "model_best_loss.bin"

# 모델 초기화 및 가중치 로드
model = SiameseModel(model_name='efficientnet_b0', out_features=64, pretrained=False)  # 모델 초기화
model.load_state_dict(torch.load(model_weights_path))
model.eval()  # 평가 모드로 설정

# Function to load and preprocess an image
def load_image(image_path):
    if image_path.startswith('http'):
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(image_path)
    
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, DIM)
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    image = transform(image).unsqueeze(0)
    return image

# Function to compare two images
def are_images_same(image_path_1, image_path_2):
    image_1 = load_image(image_path_1)
    image_2 = load_image(image_path_2)
    with torch.no_grad():
        output1, output2 = model(image_1, image_2)
    euclidean_distance = torch.nn.functional.pairwise_distance(output1, output2)
    return euclidean_distance.item()  # Smaller values indicate similar images

# Extract option data from comparison dataset
def extract_options(options, index):
    option_list = []
    
    if isinstance(options[0][index], list):
        for option in options[0][index]:
            temp = []
            if isinstance(options[1][index], list):
                for option2 in options[1][index]:
                    temp = [option, option2]
            else:
                temp = [option]
                
            if len(temp) > 0:
                option_list.append(temp)
                
    return option_list

# Match options
def check_options_match(opt1, opt2):
    # 중복 값 체크를 위한 집합 생성
    option_set = set(tuple(sub_option) for sub_option in opt2)
    print(option_set)

    # opt 내의 각 배열에 대해 확인
    for item in opt1:
        print(item)
        print(tuple([item]))
        if tuple([item]) in option_set:
            return True

    return False

# Define a threshold for considering two products as the same
threshold = 0.5  # Adjust as needed

# Lists to store the verification results
verification_results = []
num_of_matched_products = 0
num_of_option_matched_products = 0

# Loop through the verification data
for index, row in comparison_data.iterrows():
    matched_products = []
    price = []
    option_match = []
        
    image_path = project_path + 'images/tips_data/'
    
    option = extract_options(comp_opt, index)
    count = 0
    num_of_matched_model = 0
    num_of_option_matched_model = 0
    
    tikis_dict = tikis[index].replace("\"", "").replace("'", "\"").replace("\\", "")
    tikis_dict = json.loads(tikis_dict)
    lazadas_dict = lazadas[index].replace("'", "\"")
    lazadas_dict = json.loads(lazadas_dict)
    
    # Tiki check
    # check_product_match('tiki', tikis_dict, image_path, option, price, matched_products)
    
    for tiki in tikis_dict:
        image_path_comparison = image_path + row['image']
        image_path_verification = tiki['thumbnail']
        is_option_matched = 0
        
        count = count + 1
        print(f"count: {count}")
        
        if are_images_same(image_path_comparison, image_path_verification) < threshold and tiki["price"] > 1000000:
            print(row['search_word'])
            print(option)
            print(tiki['option'])
            
            price.append(tiki["price"])
            product = {
                'from': 'tiki',
                'link': tiki["link"],
                'price': tiki["price"],
                'option': tiki["option"],
            }
            
            matched_products.append(tiki)
            
            num_of_matched_model += 1
                
            if check_options_match(tiki["option"], option):
                print("matched!")
                is_option_matched = 1
                num_of_option_matched_model += 1
            
            option_match.append(is_option_matched)
        
    # Lazada check
    # check_product_match('lazada', lazadas_dict, image_path, option, price, matched_products)
        
    print(price)
    
    if len(matched_products) > 0:
        max_price = max(price)
        min_price = min(price)
    
    verification_results.append({
        'title': row['search_word'], 
        'max': max_price, 
        'min': min_price, 
        'image_name': row['image'],
        'products': matched_products
            })
    
    num_of_matched_products += num_of_matched_model
    num_of_option_matched_products += num_of_option_matched_model

# Calculate accuracy
accuracy = num_of_option_matched_products / num_of_matched_products

print(f"Accuracy: {accuracy:.2%}")

# DataFrame 생성
df_result = pd.DataFrame(verification_results)

# csv 파일로 저장
save_path = '/Users/payap/development/tips/data/'
save_file_name = 'display_data.csv'
df_result.to_csv(save_path + save_file_name, index=False)