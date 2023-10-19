from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def crawl_lazada(model, option_list):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_experimental_option("detach", True)
  
  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  
  base_url = "https://www.lazada.vn"
  results = []
  time_interval = 1.5
  scroll_height = 1000
  item_number = 1
  
  browser.get(f"{base_url}/catalog/?q={model}")
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