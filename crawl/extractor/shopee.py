from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import requests

def crawl_shopee(keyword):
  results = []
  time_interval = 1.5
  scroll_height = 1000
  item_number = 1
    
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_argument("--disable-extensions")
  options.add_experimental_option("detach", True)
  
  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  base_url = "https://shopee.vn/mall"
  
  browser.get(f"{base_url}")
  browser.implicitly_wait(100)
  soup = BeautifulSoup(browser.page_source, "html.parser")
  browser.implicitly_wait(100)
  page_block = soup.find("div", class_="shopee-mini-page-controller")
  page_list = page_block.find_all("span")
  max_page = int(page_list.pop().string)
  
  print(max_page)
  
  for index in range(1):
      browser.get(f"{base_url}/search?q={keyword}&page={index + 1}")
      browser.implicitly_wait(100)
      browser.execute_script(f"window.scrollTo(0, {1 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({1 * scroll_height}, {2 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({2 * scroll_height}, {3 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({3 * scroll_height}, document.body.scrollHeight);")
      time.sleep(time_interval)
        
      soup = BeautifulSoup(browser.page_source, "html.parser")
      items = soup.find_all('a', class_="product-item")
        
      for item in items:
        link = item['href']
        
        thumbnail_part = item.find("div", class_="thumbnail")
        thumbnail_source = thumbnail_part.find("img")
        thumbnail = thumbnail_source['src']
        
        info_part = item.find("div", class_="info")
        name_part = info_part.find("div", class_="name")
        name = name_part.find("h3").string
        
        price_part = info_part.find("div", class_="price-discount__price")
        price = int(price_part.text.strip().replace(".", "").replace("₫", "").replace(",", ""))
        
        product_data = {
            "shop": "shopee",
            "thumbnail": thumbnail.replace(",", " "),
            "name": name.replace(",", " "),
            "price": price,
            "link": f"{base_url}{link}"
        }
        
        results.append(product_data)
        """browser.get(f"{base_url}{link}")"""
        
        item_number = item_number + 1
        
  results.sort(key=lambda x: x["price"])  
  browser.close()      
  return results
