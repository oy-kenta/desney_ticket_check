#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from lxml import html
from bs4 import BeautifulSoup
import os,requests,time



CHECK_INTERVAL_SEC = 60 * 5

# url = 'https://reserve.tokyodisneyresort.jp/restaurant/calendar/?useDate=20220515&searchUseDate=20220515&adultNum=2&searchAdultNum=2&childNum=2&searchChildNum=2&stretcherCount=0&searchStretcherCount=0&wheelchairCount=0&searchWheelchairCount=0&nameCd=RBBY0&searchNameCd=RBBY0&contentsCd=04&childAgeInform=06U%7C04%7C&searchChildAgeInform=06U%7C04%7C&mealDivList=3&searchMealDivList=3&searchKeyword=&reservationStatus=0'

url = 'https://reserve.tokyodisneyresort.jp/restaurant/calendar/?searchUseDate=20220515&searchAdultNum=2&searchChildNum=2&searchChildAgeInform=04%7C06U%7C&searchWheelchairCount=0&searchStretcherCount=0&searchNameCd=RBBY0&searchKeyword=&reservationStatus=0&nameCd=RBBY0&contentsCd=04&useDate=20220515&mealDivList=3&adultNum=2&childNum=2&childAgeInform=04%7C06U%7C&wheelchairCount=0&stretcherCount=0'

# Test URL
# url = 'https://reserve.tokyodisneyresort.jp/restaurant/calendar/?useDate=20220513&searchUseDate=20220513&adultNum=2&searchAdultNum=2&childNum=2&searchChildNum=2&stretcherCount=0&searchStretcherCount=0&wheelchairCount=0&searchWheelchairCount=0&nameCd=RBPP0&searchNameCd=RBPP0&contentsCd=04&childAgeInform=06U%7C04%7C&searchChildAgeInform=06U%7C04%7C&mealDivList=3&searchMealDivList=3&searchKeyword=&reservationStatus=1'

xpath_data1 = '/html/body/div[2]/div[1]/div[3]/div[2]/div[2]/div/div/ul[1]/li'

# LINE Notify 準備
notify_url = "https://notify-api.line.me/api/notify"
access_token = open('D:\\Python\\desney_ticket_check\\dev\\access_token').read()
headers = {'Authorization': 'Bearer ' + access_token}


start_msg = "定期チェックのプロセスを開始します。"
payload = {'message': start_msg}
r = requests.post(notify_url, headers=headers, params=payload)
print(start_msg)

try:
    while True:
        browser = webdriver.Chrome(executable_path = 'D:\\Python\\lib\\chromedriver\\100\\chromedriver.exe')
        
        try:
            time.sleep(10)
            browser.get(url)
            time.sleep(10)
            html_s = BeautifulSoup(browser.page_source, 'html.parser')


            lxml_coverted_data = html.fromstring(
                str(
                    BeautifulSoup(browser.page_source, 'html.parser')
                )
            )
        except TimeoutException as e:
            print(e)
            payload = {'message': f'{e}'}
            r = requests.post(notify_url, headers=headers, params=payload)
            time.sleep(CHECK_INTERVAL_SEC * 2)
            continue
        
        finally:
            browser.quit()

        data1 = lxml_coverted_data.xpath(xpath_data1)   

        reserve_list = [ [ y.text.replace('\n','').replace(' ','') for y in x.getchildren()] for x in data1 ]
        
        print(reserve_list)
        
        check = list([])
        for ti, stt in reserve_list:
            if stt != '満席':
                check.append(ti)

        if len(check) > 0:
            ok_times = ','.join(check)
            msg = f""" 空きが出ました！ \n {ok_times} """
            payload = {'message': msg}
            r = requests.post(notify_url, headers=headers, params=payload,)
            
        time.sleep(CHECK_INTERVAL_SEC)

except Exception as e:
    payload = {'message': f'{e}'}
    r = requests.post(notify_url, headers=headers, params=payload)
    print(e)
finally :
    end_msg = "定期チェックのプロセスを終了します。"
    payload = {'message': end_msg}
    r = requests.post(notify_url, headers=headers, params=payload)
    print(end_msg)




