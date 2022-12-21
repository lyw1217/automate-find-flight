from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from app.config import *
from app.endpoint import *
from app.slack import *

def init_slack_channel(channel_name: str):
    try:
        s = SlackAPI(SLACK_KEY)
        s.channel_id = s.get_channel_id(channel_name)
        root_logger.critical(f"Initialize Slack > channel_id = {s.channel_id}")
    except Exception as e:
        root_logger.critical(f"Failed init slack > channel_name = {channel_name}, err = {e}")

    return s

def post_slack_message(s: SlackAPI, text: str):
    if len(s.channel_id) > 0 :
        try :
            res = s.post_message(s.channel_id, text)
            root_logger.critical("Send Slack Message : " + text)
            return res
        except Exception as e:
            root_logger.critical(f"Failed Send Slack Message > id : {s.channel_id}, text : {text}, err = {e}")
            res = ""
            return res
    return ""

slack = init_slack_channel(SLACK_CHANNEL)
    
def getFlight():
    def wait_until(xpath_str):
        time.sleep(0.1)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath_str)))

    # chromedriver 설정
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    driver.implicitly_wait(10)  # 페이지가 열리기까지 최대 10 seconds 초 기다리기

    # 메인 페이지 열기
    driver.get(MAIN_URL)

    # 팝업 닫기
    wait_until('//*[@id="__next"]/div/div[1]/div[9]/div/div[2]/button[1]')
    popup_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[9]/div/div[2]/button[1]')
    popup_btn.click()

    # 가는 날 클릭
    wait_until('//button[text() = "가는 날"]')
    begin_date_btn = driver.find_element(By.XPATH, '//button[text() = "가는 날"]')
    begin_date_btn.click()

    # 출발일 클릭
    wait_until('//b[text() = "26"]')
    departure_day = driver.find_elements(By.XPATH, '//b[text() = "26"]') # TODO
    departure_day[1].click()

    # 도착일 클릭
    wait_until('//b[text() = "29"]')
    arrival_day = driver.find_elements(By.XPATH, '//b[text() = "29"]') # TODO
    arrival_day[1].click()

    # 도착 도시 클릭
    wait_until('//b[text() = "도착"]')
    arrival_city = driver.find_element(By.XPATH, '//b[text() = "도착"]')
    arrival_city.click()

    # 국가 검색
    wait_until('//input[contains(@placeholder, "국가")]')
    search_input = driver.find_element(By.XPATH, '//input[contains(@placeholder, "국가")]')
    search_input.clear()
    search_input.send_keys(f"오사카\n") # TODO
    
    # 검색 첫 번째 국가 클릭
    wait_until('//mark[contains(text(), 오사카)]')
    search_result = driver.find_elements(By.XPATH, '//mark[contains(text(), 오사카)]') # TODO
    search_result[0].click()

    # 항공권 검색 클릭
    wait_until('//span[contains(text(), "항공권 검색")]')
    search = driver.find_element(By.XPATH, '//span[contains(text(), "항공권 검색")]')
    search.click()

    # 시간 필터링
    wait_until('//span[contains(text(), "시각/가격")]')
    time_filter = driver.find_element(By.XPATH, '//span[contains(text(), "시각/가격")]')
    time_filter.click()
    # 가는 날
    wait_until('//button[contains(text(), "06:00-09:00")]') # TODO
    departure_time1 = driver.find_elements(By.XPATH, '//button[contains(text(), "06:00-09:00")]')
    departure_time1[0].click()
    # 오는 날
    wait_until('//button[contains(text(), "15:00-18:00")]') # TODO
    arrival_time1 = driver.find_elements(By.XPATH, '//button[contains(text(), "15:00-18:00")]')
    arrival_time1[1].click()
    arrival_time2 = driver.find_elements(By.XPATH, '//button[contains(text(), "18:00-21:00")]')
    arrival_time2[1].click()

    # 적용
    wait_until('//button[contains(text(), "적용")]') # TODO
    confirm_btn = driver.find_element(By.XPATH, '//button[contains(text(), "적용")]')
    confirm_btn.click()

    # 출력
    wait_until('//div[contains(@class, "concurrent_ConcurrentItemContainer")]') # TODO
    confirm_btn = driver.find_elements(By.XPATH, '//div[contains(@class, "concurrent_ConcurrentItemContainer")]')

    print(confirm_btn[0].text.replace('\n',' '))
    print(confirm_btn[0].text.replace('\n',' ').split(" ")[-1].split("원")[0])
    print("")
    print(confirm_btn[1].text.replace('\n',' '))
    print(confirm_btn[1].text.replace('\n',' ').split(" ")[-1].split("원")[0])
    print("")
    print(confirm_btn[2].text.replace('\n',' '))
    print(confirm_btn[2].text.replace('\n',' ').split(" ")[-1].split("원")[0])

    result = list()

    result.append(confirm_btn[0].text.replace('\n',' '))
    result.append(confirm_btn[1].text.replace('\n',' '))
    result.append(confirm_btn[2].text.replace('\n',' '))

    return result

def findFlight():
    
    while True :
        try :
            post_slack_message(slack, "\n".join(getFlight()))
            time.sleep(1800)

        except Exception as e :
            print(e)
            print("")
            print("Error 발생, 재시도")
            time.sleep(5)
        