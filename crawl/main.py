# from extractor.shopee import crawl_shopee
import math
import pandas as pd
from extractor.tiki import crawl_tiki
from extractor.lazada import crawl_lazada

# declair
crawled_dataset = []

# csv 파일 경로
csv_file_path = '/Users/payap/development/tips/data/'
file_name = 'test_option.csv'

# csv 파일 불러오기
df = pd.read_csv(csv_file_path + file_name)
search_keywords = df['search_word'].values.tolist()
version = df['ver'].str.split('.').tolist()
options = [df['option 1'].str.split('.').tolist(), df['option 2'].str.split('.').tolist()]

for index, keyword in enumerate(search_keywords):
    models = []
    
    if isinstance(version[index], list):    
        for ver in version[index]:
            if ver == 'base':
                ver = ''
            models.append(f'{keyword} {ver}')
    else:
        models.append(keyword)
        
    option_list = []
    
    if isinstance(options[0][index], list):    
        for idx, option in enumerate(options[0][index]):
            temp = []
            if isinstance(options[1][index], list):
                for option2 in options[1][index]:
                    temp = [option, option2]
            else:
                temp = [option]
                    
            if len(temp) > 0:
                option_list.append(temp)
                         
    for model in models:
        print(model)
        print(option_list)
        tiki = crawl_tiki(model, option_list)
        lazada = crawl_lazada(model, option_list)
        # shopee = crawl_shopee(keyword)
        
        crawl_data = {
            "keyword": model,
            "tiki": tiki,
            "lazada": lazada,
            # "shopee": shopee
        }
        
        crawled_dataset.append(crawl_data)    
    
# DataFrame 생성
df_result = pd.DataFrame(crawled_dataset)

# csv 파일로 저장
save_path = '/Users/payap/development/tips/data/'
save_file_name = 'crawled_data.csv'
df_result.to_csv(save_path + save_file_name, index=False)