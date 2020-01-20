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

# 예매 날짜 정보 (Datetime 객체 생성 용)
start_year = int(config('START_YEAR'))
start_month = int(config('START_MONTH'))
start_date = int(config('START_DATE'))
start_hour = int(config('START_HOUR'))
start_min = int(config('START_MIN'))

# print(start_year)
# print(start_month)
# print(start_date)
# print(start_hour)
# print(start_min)

# 예매 날짜 정보 (예매창 날짜 선택용)
user_date = config('PLAY_DATE')
user_datetime = datetime(year = start_year, month = start_month, day = start_date, hour = start_hour, minute = start_min, second=0, microsecond=850000) 

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
pause.until(user_datetime)
# driver.refresh()
driver.get(url)

# # 예매 날짜 선택하기 (Main 화면)
# frame = wait.until(EC.presence_of_element_located((By.ID, "ifrCalendar")))
# driver.switch_to.frame(frame)
# date_elem = wait.until(EC.element_to_be_clickable((By.ID, 'CellPlayDate0')))
# bs4 = BeautifulSoup(driver.page_source, 'html.parser')
# day1 = bs4.find('td', id='CellPlayDate0').find('a')
# driver.execute_script("javascript:" + day1['onclick'] + ";")

# 예매 버튼 클릭
# driver.switch_to.default_content()
driver.find_element_by_class_name('tk_dt_btn_TArea').click()

# 예매창(팝업) 실행
driver.switch_to.window(driver.window_handles[1])

# 예매1단계: 예매날짜 선택
frame = wait.until(EC.presence_of_element_located((By.ID, 'ifrmBookStep')))
driver.switch_to.frame(frame)
# 달력 정보 가져오기
# wait.until(EC.presence_of_element_located((By.ID, 'CellPlayDate')))
bs4 = BeautifulSoup(driver.page_source, "html.parser")
calender = bs4.find_all('a', id='CellPlayDate')
# playdate = calender[0]['onclick']

####### 이 부분 실행시간이 너무 길다 이거 수정하던가 메인에서 선택하는걸로 쓰자
# 입력한 예매날짜와 일치하는 함수 찾기
for i in range(0, len(calender)):
    if "fnSelectPlayDate(" +str(i)+ ", '" +user_date+ "')" == calender[i]['onclick']:
        playdate = calender[i]['onclick']
        print("same with input date")
        break

# 해당 날짜 선택하기
print('selected date', playdate)
driver.execute_script("javascript:" + playdate + ";")

# 회차 검사하기 (이건 생략해도 될거같음)
# 다음단계, 2단계 넘어가기 기능 구현하기
driver.switch_to.default_content()
time.sleep(0.3)
driver.execute_script("javascript:fnNextStep('P');")

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
    for seat in seatList:
        # seat = seatList[i]

        # 선택한 미니맵에 좌석 존재할 경우
        if seat is not None:
            
            # 원하는 구역 좌석 선택하기
            # title 태그 안("-") 기호로 나눈 뒤
            # 뒤에서 두번째 있는 문자열(예/ B구역)로 구역을 검사하고
            # 맨 마지막에 있는 숫자(좌석 번호)를 추출해서 검사하기
            # 우선 구역 > 앞자리 우선 순으로 좌석을 선택할 수 있게 로직 짜기

            # 좌석 선택하기
            try:
                driver.execute_script(seat['onclick'] + ";")
                # 2단계 프레임 받아오기
                driver.switch_to.default_content()
                wait.until(EC.presence_of_element_located((By.ID, 'ifrmSeat')))
                frame = driver.find_element_by_id('ifrmSeat')
                driver.switch_to.frame(frame)

                # 3단계 넘어가기
                driver.execute_script("javascript:fnSelect();")
                seatCheck=True

                # 이선좌 경고창 감지
                try:
                    alert = driver.switch_to.alert()
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