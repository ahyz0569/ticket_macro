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
play_code = url.split('=')[-1]
book_url = config('BOOK_URL')

# 예매 날짜 정보 (Datetime 객체 생성 용)
start_year = int(config('START_YEAR'))
start_month = int(config('START_MONTH'))
start_date = int(config('START_DATE'))
start_hour = int(config('START_HOUR'))
start_min = int(config('START_MIN'))

# 예매 날짜 정보 (예매창 날짜 선택용)
book_date = config('BOOK_DATE')
user_datetime = datetime(year = start_year, month = start_month, day = start_date, hour = start_hour, minute = start_min, second=0, microsecond=850000) 

# 로그인 할 회원 정보
user_id = config('USER_ID')
user_pw = config('USER_PW')

# 드라이버 실행
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
time.sleep(0.5)

# 공연 기간 조회
play_period=driver.find_element_by_css_selector('.info_Lst > li > dl > dd > span').text
playDateList=[]

# 공연 기간이 2일 이상인 경우
try:
    playPeriodList= play_period.split(' ~ ')
    play_interval=int(playPeriodList[-1].split('.')[2]) - int(playPeriodList[0].split('.')[2])
    
    # 공연 기간이 2일인 경우
    if play_interval == 1:
        for date in playPeriodList:
            playDateList.append(date.replace('.',''))                    

    # 공연 기간이 3일인 경우
    elif play_interval == 2:
        for i in range(0, 3):
            ym = playPeriodList[0][:-2].replace('.','')
            f_day = playPeriodList[0][-2:].replace('.','')
            day = int(f_day) + i
            playDateList.append(ym + str(day))
    
    # 공연 기간이 4일 이상인 경우
    else:
        print('공연 기간이 4일 이상임, 예매팝업창에서 공연일정 확인 후 선택할 예정')

# 공연 기간이 1일인 경우
except:
    playDateList=play_period.replace('.','')

# 코드 구동 확인
for date in playDateList:
    print('공연일정', date)

# 예매 팝업창에서 예매 일자 선택에 사용할 변수 할당
book_index = -1
# 공연 기간과 예매일자(book_date)가 일치하는 지 확인
if playDateList is not None:
    for i in range(0, len(playDateList)):
        # 입력한 예매일자와 공연 정보가 일치하는 경우
        if book_date == playDateList[i]:
            book_index = i
            print("예매 정보 일치")
            break
    if book_index == -1:
        print('예매일정을 잘못입력함 다시입력하셈')

# 원하는 시간에 예매창 새로고침
pause.until(user_datetime)

# 예매창 실행
print(book_url + play_code + '&PlayDate=' + book_date)
book_direct_url = book_url + play_code + '&PlayDate=' + book_date
driver.get(book_direct_url)

# 다음단계, 2단계 넘어가기
driver.execute_script("javascript:fnNextStep('P');")

# 좌석 선택하기
seatCheck = False

try:
    driver.switch_to.default_content()
    frame = driver.find_element_by_id('ifrmSeat')
    driver.switch_to.frame(frame)

    # 안심예매문자 입력창 감지
    print('안심예매문자 감지 코드 실행')
    time.sleep(0.3)
    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.ID, 'divRecaptcha')))

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