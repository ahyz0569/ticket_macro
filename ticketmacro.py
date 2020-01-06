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

# 예매 URL
url = 'http://ticket.interpark.com/Ticket/Goods/GoodsInfo.asp?MN=Y&GroupCode=19019227'

# 로그인 할 회원 정보
user_id = config('USER_ID')
user_pw = config('USER_PW')

driver = webdriver.Chrome('C:/ai/program/chromedriver')
wait = WebDriverWait(driver, 10)
driver.get(url)

