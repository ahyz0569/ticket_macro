# library import
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from decouple import config
os.system("pause")

# 예매 url
url = 'http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?MN=Y&GroupCode=19019227'

# 로그인 할 회원 정보
user_id = config('USER_ID')
user_pw = config('USER_PW')

driver = webdriver.Chrome('C:/ai/program/chromedriver')
wait = WebDriverWait(driver, 10)
driver.get(url)

# 로그인하기
driver.find_element_by_css_selector('#logstatus').click()

id_input = driver.find_element_by_css_selector('#userId')
pw_input = driver.find_element_by_css_selector('#userPwd')

id_input.send_keys(user_id)
pw_input.send_keys(user_pw)

driver.find_element_by_css_selector('#btn_login').click()
