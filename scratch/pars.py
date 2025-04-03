import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib as ur
import urllib.request


url = 'https://www.google.com/search?q=%D1%87%D0%B5%D1%80%D0%BD%D0%BE%D0%B5+%D0%BF%D0%BB%D0%B0%D1%82%D1%8C%D0%B5&sca_esv=ba0413463e4e44e4&rlz=1C1GCEA_enRU1155RU1155&udm=2&biw=1578&bih=929&ei=qkLuZ_nqO7vCwPAPyseHgAM&ved=0ahUKEwj555WGtbuMAxU7IRAIHcrjATAQ4dUDCBE&uact=5&oq=%D1%87%D0%B5%D1%80%D0%BD%D0%BE%D0%B5+%D0%BF%D0%BB%D0%B0%D1%82%D1%8C%D0%B5&gs_lp=EgNpbWciGdGH0LXRgNC90L7QtSDQv9C70LDRgtGM0LUyBhAAGAcYHjIGEAAYBxgeMgYQABgHGB4yBhAAGAcYHjIGEAAYBxgeMgYQABgHGB4yBhAAGAcYHjIGEAAYBxgeMgUQABiABDIGEAAYBxgeSKMKUABYvAdwAHgAkAEAmAGhAqABrQ2qAQMyLTa4AQPIAQD4AQGYAgKgAssEmAMAkgcDMi0yoAfbK7IHAzItMrgHywQ&sclient=img'



count = 0


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)

scroll_pause_time = 1  # Пауза между прокрутками (сек)
screen_height = driver.execute_script("return window.innerHeight")  # Высота экрана
scrolls = 20

for _ in range(scrolls):
    # Прокрутка на один экран вниз
    driver.execute_script(f"window.scrollBy(0, {screen_height});")
    time.sleep(scroll_pause_time)

html = driver.page_source

# Закрываем браузер
driver.quit()

soup = BeautifulSoup(html, 'html.parser')


for img in soup.find_all('img', src=True):
    try:
        print(img['src'])
        b = requests.get(img['src'])

        count+=1
        with open(f'./black/imgpas{count}.jpg', 'wb') as file:
            for chunk in b.iter_content(1024):
                    file.write(chunk)
    except: print('non')