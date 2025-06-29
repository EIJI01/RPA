from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.maximize_window()

driver.get('http://172.188.18.251:8060/telemetry/installs')

WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".v-list-item.v-list-item--link:not(.drawer)")))

driver.find_element(By.CSS_SELECTOR, "button.v-btn i.mdi-filter-variant").click()
time.sleep(1)

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.v-autocomplete"))).click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.v-autocomplete input"))).send_keys("test-qr-performance-app")
time.sleep(1)

driver.find_element(By.XPATH, "//div[contains(text(), 'test-qr-performance-app')]").click()
time.sleep(1)

driver.find_element(By.CSS_SELECTOR, "button.v-btn i.mdi-dots-vertical.mdi.v-icon").click()
time.sleep(1)

driver.find_element(By.XPATH, "//*[@id='v-menu-3']/div/div/div[2]/div/div/div").click()
time.sleep(1)

driver.find_element(By.XPATH, "//div[contains(text(), '100')]").click()
time.sleep(2)

WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, "//*[@id='app']/div/div/main/div[1]/div[3]/div/div[2]/nav/ul/li"))
)

number_of_page = driver.find_elements(By.CSS_SELECTOR, ".v-pagination__list .v-btn__content")
last_page = int(number_of_page[-2].text) if len(number_of_page) > 1 else 1
time.sleep(1)

columns = ["machine_name", "sub_title_1", "sub_title_2", "sub_title_action_1", "sub_title_action_2", "date"]

df = pd.DataFrame(columns=columns)

for page in range(1, last_page + 1):
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[@id='app']/div/div/main/div[1]/div[2]/a"))
    )
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    headers = soup.find_all('div', class_="v-list-subheader")
    page_data = []

    for i in range(len(headers)):
        header = headers[i]
        date = header.get_text(strip=True)
        elements = []
        if i < len(headers) - 1:
            next_header = headers[i+1]
            current = header.find_next_sibling()
            while current and current != next_header:
                if current.name == 'a' and 'v-list-item' in current.get('class', []):
                    elements.append(current)
                current = current.find_next_sibling()
        else:
            elements = header.find_all_next('a', class_='v-list-item')
    
        for element in elements:
            title = element.select_one(".v-list-item-title").text if element.select_one(".v-list-item-title") else "N/A"
            sub_title_1 = element.select_one(".v-list-item-subtitle.w-25").text if element.select_one(".v-list-item-subtitle.w-25") else "N/A"
            sub_title_2 = element.select_one(".v-list-item-subtitle.w-75").text if element.select_one(".v-list-item-subtitle.w-75") else "N/A"
            sub_title_action_1 = element.select_one(".v-list-item__append .subtitle-action span").text if element.select_one(".v-list-item__append .subtitle-action span") else "N/A"
            sub_title_action_2 = element.select(".v-list-item__append .subtitle-action")[1].text if len(element.select(".v-list-item__append .subtitle-action")) > 1 else "N/A"
            
            page_data.append({
                "machine_name": title, 
                "sub_title_1": sub_title_1, 
                "sub_title_2": sub_title_2, 
                "sub_title_action_1": sub_title_action_1, 
                "sub_title_action_2": sub_title_action_2,
                "date": date
            })
    
    
    df = pd.concat([df, pd.DataFrame(page_data)], ignore_index=True)
    if page < last_page:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "nav > ul > li.v-pagination__next"))).click()
        time.sleep(2)

df.to_csv('output_data.csv', index=False, encoding='utf-8-sig')
print("บันทึกไฟล์สำเร็จ: output_data.csv")
driver.close()