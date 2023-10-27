from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random

def generate_random_headers():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/100.0.4896.85 Mobile/15E148 Safari/604.1"
    ]
    
    accept_languages = ['en-US', 'en-GB', 'es-ES', 'fr-FR']
    referer_sites = [
        'https://www.google.com/', 
        'https://www.facebook.com/', 
        'https://www.youtube.com/'
        ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": random.choice(accept_languages),
        "Referer": random.choice(referer_sites)
    }
    
    return headers

def crawl_lazada(model, option_list):
  options = Options()
  
  # 랜덤 헤더 생성
  headers = generate_random_headers()
  
  # User-Agent, Accept-Language, Referer 설정
  options.add_argument(f"user-agent={headers['User-Agent']}")
  options.add_argument(f"lang={headers['Accept-Language']}")
  options.add_argument(f"referer={headers['Referer']}")
  
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--headless")
  options.add_experimental_option("detach", True)
  
  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  
  base_url = "https://www.lazada.vn"
  results = []
  time_interval = round(random.uniform(0, 5), 2)
  scroll_height = 1000
  item_number = 1
  
  time.sleep(time_interval)
  browser.get(f"{base_url}/catalog/?q={model}")
  time.sleep(time_interval)
  browser.execute_script(f"window.scrollTo(0, {1 * scroll_height});")
  time.sleep(time_interval)
  browser.execute_script(f"window.scrollTo({1 * scroll_height}, {2 * scroll_height});")
  time.sleep(time_interval)
    
  soup = BeautifulSoup(browser.page_source, "html.parser")
  items = soup.find_all('div', class_="qmXQo")
    
  for item in items:
    thumbnail_part = item.find('div', class_="_95X4G")  
    link = thumbnail_part.find('a')['href']    

    thumbnail_source = thumbnail_part.find("img")
    thumbnail = thumbnail_source['src']
    
    info_part = item.find("div", class_="buTCk")
    name_part = info_part.find("a")
    name = name_part['title']
    print(name)
    
    price_part = info_part.find("span", class_="ooOxS")
    price = int(price_part.text.strip().replace(".", "").replace("₫", "").replace(",", ""))
    
    if len(option_list) > 0:
      option = find_matching_option(name, option_list)
    else:
      option = []
    
    product_data = {
        "thumbnail": thumbnail.replace(",", " "),
        "name": name.replace(",", " "),
        "price": price,
        "link": f"{link}",
        "option": option,
    }
    
    results.append(product_data)
    """browser.get(f"{base_url}{link}")"""
    
    item_number = item_number + 1
        
  results.sort(key=lambda x: x["price"])  
  browser.close()      
  return results

def find_matching_option(name, option_list):
    # 정확한 문자열 매칭 우선
    for option in option_list:
        if isinstance(option, list):
            for sub_option in option:
                if sub_option in name:
                    return option
        elif option in name:
            return option
    
    # 부분적으로 겹치는 문자열 예외 처리
    for option in option_list:
        if isinstance(option, list):
            for sub_option in option:
                if sub_option in name:
                    return option
        elif option in name:
            return option
    
    # 일치하는 것이 없으면 첫 번째 옵션을 기본값으로 사용
    return option_list[0]