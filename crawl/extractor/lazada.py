from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def crawl_lazada(keyword):
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
  
  browser.get(f"{base_url}/catalog/?q={keyword}")
  soup = BeautifulSoup(browser.page_source, "html.parser")
  browser.implicitly_wait(100)
  page_block = soup.find("div", class_="e5J1n")
  page_list = page_block.find_all("li")
  page_list.pop()
  max_page = int(page_list.pop().string)
  
  for index in range(1):
      browser.get(f"{base_url}/catalog/?page={index + 1}&q={keyword}")
      browser.execute_script(f"window.scrollTo(0, {1 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({1 * scroll_height}, {2 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({2 * scroll_height}, {3 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({3 * scroll_height}, {4 * scroll_height});")
      time.sleep(time_interval)
      browser.execute_script(f"window.scrollTo({4 * scroll_height}, document.body.scrollHeight);")
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
        
        product_data = {
            "shop": "tiki",
            "thumbnail": thumbnail.replace(",", " "),
            "name": name.replace(",", " "),
            "price": price,
            "link": f"{link}"
        }
        
        results.append(product_data)
        """browser.get(f"{base_url}{link}")"""
        
        item_number = item_number + 1
        
  results.sort(key=lambda x: x["price"])  
  browser.close()      
  return results
  
      