from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
TIME_OUT = 10

def data_to_excel(names, addrs, tels):
    df = pd.DataFrame({'Name': names, 'Address': addrs, 'Tel': tels})

    try:
        existing_df = pd.read_excel('output.xlsx')
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel('output.xlsx', index=False)

    except FileNotFoundError:
        df.to_excel('output.xlsx', index=False)

def open_browser():
    url = 'http://www.childinfo.go.kr/main.jsp'
    driver.get(url)
    driver.maximize_window()

    wait = WebDriverWait(driver, TIME_OUT)
    button_map = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div > div > div > div.sec_body > div.sec2 > a')))
    button_map.click()


    button_city = wait.until(EC.presence_of_element_located((By.ID, 'ctprvn')))
    select = Select(button_city)
    select.select_by_visible_text('경기도')
    time.sleep(1)

    button_signgu = wait.until(EC.presence_of_element_located((By.ID, 'signgu')))
    select = Select(button_signgu)
    select.select_by_visible_text('평택시')
    time.sleep(1)

    button_search = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#sfrm > div.list_srch.mt15 > div > a > img')))
    button_search.click()
    time.sleep(3)


def parse_data():
    e_ul = driver.find_element(By.CLASS_NAME, 'result_list')
    e_lis = e_ul.find_elements(By.CLASS_NAME, 'divNurseryList')

    names = []
    addrs = []
    tels = []
    for li in e_lis:
        info_container = li.find_element(By.CLASS_NAME, 'list.pt6')
        tit = info_container.find_element(By.CLASS_NAME, 'tit')
        name = tit.find_element(By.CSS_SELECTOR, 'a:nth-of-type(2)').text
        txt_info = info_container.find_element(By.CLASS_NAME, 'txt_info')
        addr = txt_info.find_element(By.CLASS_NAME, 'txt5').text
        tel = txt_info.find_element(By.CLASS_NAME, 'txt10').text

        names.append(name)
        addrs.append(addr)
        tels.append(tel)
    data_to_excel(names, addrs, tels)

def next_page():
    e_page_skip = driver.find_element(By.CLASS_NAME, 'page_skip')
    cur_index = int(e_page_skip.find_element(By.CLASS_NAME, 'on').text)

    button_next = e_page_skip.find_element(By.XPATH, ".//a[@title='다음']")
    button_next.click()
    wait = WebDriverWait(driver.find_element(By.CSS_SELECTOR, '#divList'), TIME_OUT)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#popfrm')))

    e_page_skip = driver.find_element(By.CLASS_NAME, 'page_skip')
    next_index = int(e_page_skip.find_element(By.CLASS_NAME, 'on').text)

    return cur_index == next_index

def auto():
    open_browser()
    parse_data()
    while not next_page():
        parse_data()
    print('작업 끝!')
    driver.close()