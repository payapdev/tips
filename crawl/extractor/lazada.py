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
  # page_block = soup.find("div", class_="e5J1n")
  # page_list = page_block.find_all("li")
  # page_list.pop()
  # max_page = int(page_list.pop().string)
  
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
  
def crawl_options(link):
  options = Options()
  options.add_argument("--no-sandbox")
  options.add_argument("--disable-dev-shm-usage")
  options.add_experimental_option("detach", True)
  
  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
  options_wrapper = {}
  time_interval = 1.5
  browser.get(f"{link}")
  act = ActionChains(browser)
  soup = BeautifulSoup(browser.page_source, "html.parser")
  wrapper = soup.find('div', class_="sku-selector")
  items = wrapper.find_all('div', class_="sku-prop")
  
  for index, item in enumerate(items):
    option_name = item.find("h6", class_="section-title")
    option_values = []
    
    if option_name:
      option_name = option_name.text.strip()
      print(option_name)
    else:
      continue
    
    option_values.append(item.find("span", class_="sku-name").text.strip())
    
    # img_wraps = item.find_all("span", class_="sku-variable-img-wrap")
    # text_wraps = item.find_all("span", class_="sku-variable-name")
    
    img_wraps = browser.find_elements(By.CLASS_NAME, "sku-variable-img-wrap")
    text_wraps = browser.find_elements(By.CLASS_NAME, "sku-variable-name")
    
    if img_wraps:
      for img_wrap in img_wraps:
        print(img_wrap)
        act.click(img_wrap).perform()
        time.sleep(time_interval)
        
        update = BeautifulSoup(browser.page_source, "html.parser")
        options = update.find_all('div', class_="sku-prop")
        
        option_value = options[index].find("span", class_="sku-name").text.strip()
        option_values.append(option_value) 
      
    elif text_wraps:
      for text_wrap in text_wraps:
        text_wrap.click()
        time.sleep(time_interval)
        print("text")
      
        option_value = item.find("span", class_="sku-name").text.strip()
        option_values.append(option_value)
    
    options_wrapper[option_name] = option_values
    
  print(options_wrapper)
  browser.close()
    
  return options_wrapper
  
crawl_options("https://www.lazada.vn/products/sale-1010-iphone-15-hang-chinh-hang-vna-i2417259469-s11887253976.html?")