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
    
def get_flight(city, departure_day, departure_time, arrival_day, arrival_time):
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
    xpath = '//*[@id="__next"]/div/div[1]/div[9]/div/div[2]/button[1]'
    wait_until(xpath)
    popup_btn = driver.find_element(By.XPATH, xpath)
    popup_btn.click()

    # 가는 날 클릭
    xpath = '//button[text() = "가는 날"]'
    wait_until(xpath)
    begin_date_btn = driver.find_element(By.XPATH, xpath)
    begin_date_btn.click()

    try:
        # 출발일 파싱
        dep_year = departure_day.split('-')[0]
        dep_month = departure_day.split('-')[1]
        dep_day = departure_day.split('-')[2]
        # 출발일 클릭
        xpath = f'//div[contains(@class, "month")]'
        dep_elems = driver.find_elements(By.XPATH, xpath)
        find_flag = False
        i = 0
        for dep_elem in dep_elems :
            if f"20{dep_year}.{dep_month}." in dep_elem.text.split('\n') :
                xpath = f'//b[text() = "{dep_day}"]'
                departure_day_btn = driver.find_elements(By.XPATH, xpath)
                departure_day_btn[i].click()
                find_flag = True
                break
            else :
                i += 1
        if find_flag == False :
            raise Exception("Not found departure datetime")
    except Exception as e :
        res = "출발일이 잘못 설정되었습니다."
        root_logger.critical(f"{res}, exception = {e}")
        return res
    
    try:
        # 도착일 파싱
        arr_year = arrival_day.split('-')[0]
        arr_month = arrival_day.split('-')[1]
        arr_day = arrival_day.split('-')[2]
        # 도착일 클릭
        xpath = f'//div[contains(@class, "month")]'
        arr_elems = driver.find_elements(By.XPATH, xpath)
        find_flag = False
        i = 0
        for arr_elem in arr_elems :
            if f"20{arr_year}.{arr_month}." in arr_elem.text.split('\n') :
                xpath = f'//b[text() = "{arr_day}"]'
                arrival_day_btn = driver.find_elements(By.XPATH, xpath)
                arrival_day_btn[i].click()
                find_flag = True
                break
            else :
                i += 1
        if find_flag == False :
            raise Exception("Not found arrival datetime")
    except Exception as e :
        res = "도착일이 잘못 설정되었습니다."
        root_logger.critical(f"{res}, exception = {e}")
        return res
    
    # 도착 도시 클릭
    xpath = '//b[text() = "도착"]'
    wait_until(xpath)
    arrival_city_btn = driver.find_element(By.XPATH, xpath)
    arrival_city_btn.click()

    # 국가 검색
    xpath = '//input[contains(@placeholder, "국가")]'
    wait_until(xpath)
    search_input = driver.find_element(By.XPATH, xpath)
    search_input.clear()
    search_input.send_keys(f"{city}\n")
    
    # 검색 첫 번째 국가 클릭
    try :
        xpath = f'//mark[contains(text(), {city})]'
        wait_until(xpath)
        search_result = driver.find_elements(By.XPATH, xpath)
        search_result[0].click()
    except Exception as e :
        res = "국가가 잘못 설정되었습니다."
        root_logger.critical(f"{res}, exception = {e}")
        return res

    # 항공권 검색 클릭
    xpath = '//span[contains(text(), "항공권 검색")]'
    wait_until(xpath)
    search_btn = driver.find_element(By.XPATH, xpath)
    search_btn.click()

    # 시간 필터링 클릭
    xpath = '//span[contains(text(), "시각/가격")]'
    wait_until(xpath)
    time_filter = driver.find_element(By.XPATH, xpath)
    time_filter.click()
    
    try :
        # 가는 날 시간대 파싱
        for t in departure_time.split(',') :
            t = t.split('-')    
            # 가는 날 시간대 클릭
            xpath = f'//button[contains(text(), "{t[0]}:00-{t[1]}:00")]'
            wait_until(xpath)
            departure_time_btn = driver.find_elements(By.XPATH, xpath)
            departure_time_btn[0].click()
    except Exception as e :
        res = "가는 날 시간대가 잘못 설정되었습니다."
        root_logger.critical(f"{res}, exception = {e}")
        return res

    try :
        # 오는 날 시간대 파싱
        for t in arrival_time.split(',') :
            t = t.split('-')    
            # 오는 날 시간대 클릭
            xpath = f'//button[contains(text(), "{t[0]}:00-{t[1]}:00")]'
            wait_until(xpath)
            arrival_time_btn = driver.find_elements(By.XPATH, xpath)
            arrival_time_btn[1].click()
    except Exception as e :
        res = "오는 날 시간대가 잘못 설정되었습니다."
        root_logger.critical(f"{res}, exception = {e}")
        return res

    # 적용 클릭
    xpath = '//button[contains(text(), "적용")]'
    wait_until(xpath)
    confirm_btn = driver.find_element(By.XPATH, xpath)
    confirm_btn.click()

    # 결과 파싱
    xpath = '//div[contains(@class, "concurrent_ConcurrentItemContainer")]'
    wait_until(xpath)
    items = driver.find_elements(By.XPATH, xpath)

    result = list()
    
    avoid_company = "없음"
    for val in items :
        if avoid_company not in val.text :
            item = val.text.replace('\n',' ').split(' ')
            print(f"len(result)={len(result)}, len(item)={len(item)}, {item}")
            if len(item) == 14 :
                item_str = f'''
🛩️\t{item[11]}\t{item[13]}
🛫 {item[0]:　<9}\t{item[1]:　<9}\t{item[2]:　<9}\t{item[3]:　<2}\t{item[4]:　<4} {item[5]:　<3}
🛬 {item[0]:　<9}\t{item[6]:　<9}\t{item[7]:　<9}\t{item[8]:　<2}\t{item[9]:　<4} {item[10]:　<3}
'''
            elif len(item) == 15 or len(item) == 16 :
                item_str = f'''
🛩️\t{item[12]}\t{item[14]}
🛫 {item[0]:　<9}\t{item[1]:　<9}\t{item[2]:　<9}\t{item[3]:　<2}\t{item[4]:　<4} {item[5]:　<3}
🛬 {item[6]:　<9}\t{item[7]:　<9}\t{item[8]:　<9}\t{item[9]:　<2}\t{item[10]:　<4} {item[11]:　<3}
'''
            else :
                item_str = "🛩️\t" + val.text.replace('\n',' ')
            result.append(item_str)
            if len(result) > 3 :
                break

    result.append(f"{driver.current_url}")

    return ''.join(result)

def find_flight(city, departure_day, departure_time, arrival_day, arrival_time):

    while True :
        try :
            res = get_flight(city, departure_day, departure_time, arrival_day, arrival_time)
            post_slack_message(slack, res)
            return res

        except Exception as e :
            print(e)
            print("")
            print("Error 발생, 재시도")
            time.sleep(5)