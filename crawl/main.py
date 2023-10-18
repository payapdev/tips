# from extractor.shopee import crawl_shopee
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
print("start!")
print(version)
print(options)

for index, keyword in enumerate(search_keywords):
    print(keyword)
    models = []
    
    for ver in version[index]:
        if ver == 'base':
            ver = ''
        models.append(f'{keyword} {ver}')
    print(models)
        
    option_list = []
    for option in options:
        temp = []
        if len(option[0]) != 0:
            if len(option[1]) != 0:
                for o1 in option[0]:
                    for o2 in option[1]:
                        temp = [o1, o2]
            else:
                for o1 in option[0]:
                    temp = [o1]
            option_list.append(temp)   
                         
    for model in models:
        tiki = crawl_tiki(model, option_list)
        # lazada = crawl_lazada(model, option_list)
        # shopee = crawl_shopee(keyword)
        
        crawl_data = {
            "keyword": model,
            "tiki": tiki,
            # "lazada": lazada,
            # "shopee": shopee
        }
        
        crawled_dataset.append(crawl_data)    
    
    
    
print(crawled_dataset)
# DataFrame 생성
df_result = pd.DataFrame(crawled_dataset)

# csv 파일로 저장
save_path = '/Users/payap/development/tips/data/test_option_crawled_data.csv'
df_result.to_csv(save_path, index=False)