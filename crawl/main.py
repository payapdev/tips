# from extractor.shopee import crawl_shopee
import pandas as pd
from extractor.tiki import crawl_tiki
from extractor.lazada import crawl_lazada

# declair
crawled_dataset = []

# csv 파일 경로
csv_file_path = '/Users/payap/development/tips/data/tips_data.csv'

# csv 파일 불러오기
df = pd.read_csv(csv_file_path)
search_keywords = df['search_word'].values.tolist()
# search_keywords = [ "logitech g102", "apple pencil",]

for keyword in search_keywords:
    print(keyword)
    tiki = crawl_tiki(keyword)
    lazada = crawl_lazada(keyword)
    # shopee = crawl_shopee(keyword)
    
    crawl_data = {
        "keyword": keyword,
        "tiki": tiki,
        "lazada": lazada,
        # "shopee": shopee
    }
    
    crawled_dataset.append(crawl_data)
    
print(crawled_dataset)
# DataFrame 생성
df_result = pd.DataFrame(crawled_dataset)

# csv 파일로 저장
save_path = '/Users/payap/development/tips/data/crawled_data.csv'
df_result.to_csv(save_path, index=False)