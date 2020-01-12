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
from bs4 import BeautifulSoup

## 예매 정보
# 예매 url
url = config('URL')

# 예매 날짜
start_year = int(config('START_YEAR'))
start_month = int(config('START_MONTH'))
start_date = int(config('START_DATE'))
start_hour = int(config('START_HOUR'))
start_min = int(config('START_MIN'))

# 로그인 할 회원 정보
user_id = config('USER_ID')
user_pw = config('USER_PW')


driver = webdriver.Chrome('C:/ai/program/chromedriver')
wait = WebDriverWait(driver, 10)
driver.get(url)

# 로그인하기
driver.find_element_by_css_selector('#logstatus').click()
# WebDriverWait(driver, 10)
driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
time.sleep(0.5)

id_input = driver.find_element_by_id('userId').send_keys(user_id)
pw_input = driver.find_element_by_id('userPwd').send_keys(user_pw)

driver.find_element_by_css_selector('#btn_login').click()

# 원하는 시간에 예매창 새로고침
pause.until(datetime(start_year, start_month, start_date, start_hour, start_min, 0))
# driver.refresh()
driver.get(url)

# 예매 날짜 선택하기
frame = wait.until(EC.presence_of_element_located((By.ID, "ifrCalendar")))
driver.switch_to.frame(frame)

date_elem = wait.until(EC.element_to_be_clickable((By.ID, 'CellPlayDate0')))
# date_elem.click()
driver.execute_script("javascript:fnSelectPlayDate(0, '20200404');")

# 예매 버튼 클릭
driver.switch_to.default_content()
driver.find_element_by_class_name('tk_dt_btn_TArea').click()

# 예매창(팝업) 실행
driver.switch_to.window(driver.window_handles[1])

# 좌석 선택하기
seatCheck = False

try:
    driver.switch_to.default_content()
    frame = driver.find_element_by_id('ifrmSeat')
    driver.switch_to.frame(frame)

    # 안심예매문자 입력창 감지
    wait.until(EC.invisibility_of_element_located((By.ID, 'divRecaptcha')))

    # 미니맵 존재여부 검사
    try:
        wait.until(EC.presence_of_element_located((By.ID, 'ifrmSeatView')))
        frame = driver.find_element_by_id('ifrmSeatView')
        driver.switch_to.frame(frame)
        wait.until(EC.presence_of_element_located((By.NAME, 'Map')))
        bs4 = BeautifulSoup(driver.page_source, 'html.parser')
        elem = bs4.find('map')
    except:
        elem = None

    # time.sleep(0.5)

    # 좌석 프레임 받아오기
    driver.switch_to.default_content()
    wait.until(EC.presence_of_element_located((By.ID, 'ifrmSeat')))
    frame = driver.find_element_by_id('ifrmSeat')
    driver.switch_to.frame(frame)
    frame = driver.find_element_by_id('ifrmSeatDetail')
    driver.switch_to.frame(frame)

    # 좌석 정보 읽기    
    bs4 = BeautifulSoup(driver.page_source, 'html.parser')
    seatList = bs4.find_all('img', class_='stySeat')
    print('available seat list number: {}'.format(len(seatList)))

    # 좌석 존재 여부 체크
    for i in range(0, len(seatList)):
        seat = seatList[i]

        # 선택한 미니맵에 좌석 존재할 경우
        if seat is not None:            
            # 좌석 선택하기
            try:
                driver.execute_script(seat['onclick'] + ";")
                # 2단계 프레임 받아오기
                driver.switch_to_default_content()
                wait.until(EC.presence_of_element_located((By.ID, 'ifrmSeat')))
                frame = driver.find_element_by_id('ifrmSeat')
                driver.switch_to.frame(frame)

                # 3단계 넘어가기
                driver.execute_script("javascript:fnSelect();")
                seatCheck=True
                # 이선좌 경고창 감지
                try:
                    alert = driver.switch_to_alert()
                    alert.accept()
                    time.sleep(0.5)
                    seatCheck = False
                    continue
                except:
                    elem = ''
                    print('no alert window or got exception')

                break

            except:
                print('try to move to fianl stage. but failed: {}'.format(seat))
        
        # 선택한 미니맵에 좌석이 존재하지 않는 경우 
        # else:
        #     driver.switch_to.default_content()
        #     frame = driver.find_element_by_id('ifrmSeat')
        #     driver.switch_to.frame(frame)
        #     frame = driver.find_element_by_id('ifrmSeatView')
        #     driver.switch_to.frame(frame)
        #     wait.until(EC.presence_of_element_located((By.NAME, 'Map')))
        #     bs4 = BeautifulSoup(driver.page_source, 'html.parser')
        #     map = bs4.find('map')

except:
    print('got unexpected except')