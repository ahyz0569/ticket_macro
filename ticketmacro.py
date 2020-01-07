# library import
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pause
from decouple import config


## 예매 정보
# 예매 url
url = 'http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?GoodsCode=19018974#'
# 예매 날짜
start_year = 2019
start_month = 1
start_date = 7
start_hour = 11
start_min = 50

# 로그인 할 회원 정보
user_id = config('USER_ID')
user_pw = config('USER_PW')


driver = webdriver.Chrome('C:/ai/program/chromedriver')
wait = WebDriverWait(driver, 10)
driver.get(url)

# 로그인하기
driver.find_element_by_css_selector('#logstatus').click()
WebDriverWait(driver, 10)
driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
time.sleep(0.5)

id_input = driver.find_element_by_id('userId').send_keys(user_id)
pw_input = driver.find_element_by_id('userPwd').send_keys(user_pw)

driver.find_element_by_css_selector('#btn_login').click()

# 원하는 시간에 예매창 새로고침
pause.until(datetime(start_year, start_month, start_date, start_hour, start_min, 00))
driver.get(url)

# 예매 날짜 선택하기
frame = wait.until(EC.presence_of_element_located((By.ID, "ifrCalendar")))
driver.switch_to.frame(frame)

date_elem = wait.until(EC.element_to_be_clickable((By.ID, 'CellPlayDate0')))
date_elem.click()

# 예매 버튼 클릭
driver.switch_to.default_content()
driver.find_element_by_class_name('tk_dt_btn_TArea').click()

driver.switch_to_window(driver.window_handles[1])

