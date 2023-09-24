from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio

async def playwright_shopee(keyword):
    async with async_playwright() as playwright:
        base_url = "https://shopee.vn/mall"
        
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(f"{base_url}")
        print("searching")
        
        html_content = await page.content()
        asyncio.sleep(100)
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        if soup.find("div", class_="home-popup") != None:
            print("popup")
            popups = soup.find_all("div", class_="home-popup")
            for popup in popups:
              await page.click(f"div[class=shopee-popup__close-btn]")
              print("popup close")
            
        print(soup)
        search_form = soup.find("form", class_="shopee-searchbar")
        print(search_form)
        search_bar = search_form.find("input", class_="shopee-searchbar-input__input")
        print(search_bar)
        """search_bar["value"] = f"{keyword}"
        search_button = soup.find("button", class_="btn btn-solid-primary btn--s btn--inline shopee-searchbar__search-button")
        print(search_button)
        search_button_id = search_button.get("class")
        print(search_button_id)
        await page.click(f"button[class='{search_button_id}']")
        await asyncio.sleep(3)"""
        
        """page_block = soup.find("div", class_="shopee-mini-page-controller")
        page_list = page_block.find_all("span")
        max_page = int(page_list.pop().string)
        print(max_page)"""
        
        await browser.close()


asyncio.run(playwright_shopee("iphone"))