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

def crawl_tiki(model, option_list):
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
  
  base_url = "https://tiki.vn"
  results = []
  time_interval = round(random.uniform(0, 5), 2)
  scroll_height = 800
  item_number = 1
  
  browser.get(f"{base_url}/search?q={model}")
  browser.implicitly_wait(100)
  browser.execute_script(f"window.scrollTo(0, {1 * scroll_height});")
  time.sleep(time_interval)
  browser.execute_script(f"window.scrollTo({1 * scroll_height}, {2 * scroll_height});")
  time.sleep(time_interval)
    
  soup = BeautifulSoup(browser.page_source, "html.parser")
  items = soup.find_all('a', class_="product-item")
    
  for item in items:
    link = item['href']
    
    thumbnail_part = item.find("div", class_="thumbnail")
    thumbnail_source = thumbnail_part.find("img")
    thumbnail = thumbnail_source['srcset'].split()[0]
    
    info_part = item.find("div", class_="info")
    name_part = info_part.find("div", class_="name")
    name = name_part.find("h3").string
    
    price_part = info_part.find("div", class_="price-discount__price")
    price = int(price_part.text.strip().replace(".", "").replace("₫", "").replace(",", ""))
    
    if len(option_list) > 0:
      option = find_matching_option(name, option_list)
    else:
      option = []  
    
    
    product_data = {
        "thumbnail": thumbnail.replace(",", " "),
        "name": name.replace(",", " "),
        "price": price,
        "link": f"{base_url}{link}",
        "option": option,
    }
    
    results.append(product_data)
    # browser.get(f"{base_url}{link}")
    
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
  
def crawl_options(link):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_experimental_option("detach", True)
  
  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  
  options_wrapper = {}
  browser.get(f"{link}")
  soup = BeautifulSoup(browser.page_source, "html.parser")
  wrapper = soup.find('div', class_="styles__ProductOptionsWrapper-sc-18rzur4-0 jZCObm")
  items = wrapper.find_all('div', class_="styles__VariantSelectWrapper-sc-1pikfxx-0 heEOGZ")
  
  for item in items:
    option_name = item.find("p", class_="option-name").text.strip()
    options_values = []
    active_values = item.find_all("div", class_="styles__OptionButton-sc-1ts19ms-0 iuHuWV active")
    inactive_values = item.find_all("div", class_="styles__OptionButton-sc-1ts19ms-0 iuHuWV")
    
    for value in active_values:
      options_values.append(value.text.strip())
      
    for value in inactive_values:
      options_values.append(value.text.strip())
    
    options_wrapper[option_name] = options_values
    
  print(options_wrapper)
  browser.close()
    
  return options_wrapper
  