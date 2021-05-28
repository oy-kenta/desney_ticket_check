#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import datetime
from selenium import webdriver
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import os,requests,time


# In[2]:


CHECK_INTERVAL_SEC = 60 * 5
CHECK_DOW = ['土','日']
ticket_sales_url = 'https://www.tokyodisneyresort.jp/ticket/sales_status/'
table_id = 'calendarTableSp ticketStock'


# In[3]:


# LINE Notify 準備
url = "https://notify-api.line.me/api/notify"
access_token = os.environ['LINEN_TOKEN']
headers = {'Authorization': 'Bearer ' + access_token}


# In[4]:


year_monthes = [datetime.date.today().strftime('%Y%m'),(datetime.date.today() + pd.DateOffset(days=31)).strftime('%Y%m')]


# In[5]:


browser = webdriver.Chrome(executable_path = 'D:\\Python\\lib\\chromedriver.exe')


# In[6]:


table_df_old = dict()


# In[7]:


# ページ情報取得
# year_month = year_monthes[1]
year_month = '202105'


# In[8]:


start_msg = "定期チェックのプロセスを開始します。"
payload = {'message': start_msg}
r = requests.post(url, headers=headers, params=payload)
print(start_msg)

try:
    while True:
        browser.get(ticket_sales_url+year_month)
        html = BeautifulSoup(browser.page_source, 'html.parser')
        table = html.findAll(class_ = table_id)[0]

        table_df = None
        for row in table.findAll(['tr']):

            if len(row.findAll('th')) > 0:
                columns = []
                for th in row.findAll('th'):
                    columns.append(th['class'][0])

                table_df = pd.DataFrame(columns=columns)

            elif len(row.findAll('td')) > 0:
                day = row.findAll('td')[0].find('div').get_text()      
                tdl_status = ' '.join(row.findAll('td')[1]['class'])
                tds_status = ' '.join(row.findAll('td')[2]['class'])
                data = [day,tdl_status,tds_status]

                table_df = table_df.append(dict(zip(table_df.columns,data)), ignore_index=True)


        table_df = (
            table_df
            .pipe(lambda df: 
                  df[['tdl','tds']]
                  .join(
                      df.day.apply(lambda x: pd.Series(data=[pd.to_datetime(year_month+x.split('(')[0].zfill(2)),x.split('(')[1][0]],index=['date','dow'] ))
                  )
                 )
            .set_index('date')
        )

        # table_df_old に値が格納されている場合
        if year_month in table_df_old.keys():
            # TDL の差分取得
            tdl_diff = (
                table_df_old[year_month].loc[lambda df: df.dow.isin(CHECK_DOW)]
                .join(table_df[['tdl','tds']],rsuffix='_new')
                .loc[lambda df: (df.tdl != df.tdl_new) & (df.tdl_new.isin(['tdl','tdl is-few']))]
                .replace({'tdl':'〇','tdl is-few':'△'})
                .loc[:,['dow','tdl_new']]
            )

            tdl_msg = ""
            if tdl_diff.shape[0] > 0:

                for idx, row in tdl_diff.iterrows():
                    tdl_msg = tdl_msg + f" {idx.strftime('%m/%d')} ({row.dow}):{row.tdl_new} \n"
            tdl_msg

            # TDS の差分取得
            tds_diff = (
                table_df_old[year_month].loc[lambda df: df.dow.isin(CHECK_DOW)]
                .join(table_df[['tdl','tds']],rsuffix='_new')
                .loc[lambda df: (df.tds != df.tds_new) & (df.tds_new.isin(['tds','tds is-few']))]
                .replace({'tds':'〇','tds is-few':'△'})
                .loc[:,['dow','tds_new']]
            )

            tds_msg = ""
            if tds_diff.shape[0] > 0:
                for idx, row in tds_diff.iterrows():
                    tds_msg = tds_msg + f" {idx.strftime('%m/%d')} ({row.dow}):{row.tds_new} \n"
            tds_msg

            # LINE 送信メッセージの作成
            msg = ""

            if (tdl_msg != "") | (tds_msg != ""):
                msg = "チケットが購入可能になりました。\n"
                if (tdl_msg != ""):
                    msg = msg + "ディズニーランド\n"
                    msg = msg + tdl_msg

                if (tds_msg != ""):
                    msg = msg + "ディズニーシー\n"
                    msg = msg + tds_msg

                msg = msg + ticket_sales_url+year_month

            if msg != "":
                payload = {'message': msg}
                r = requests.post(url, headers=headers, params=payload)
                print(msg)

        table_df_old[year_month] = table_df.copy()

        time.sleep(CHECK_INTERVAL_SEC)
except Exception as e:
    payload = {'message': f'{e}'}
    r = requests.post(url, headers=headers, params=payload)
    print(e)
finally :
    end_msg = "定期チェックのプロセスを終了します。"
    payload = {'message': end_msg}
    r = requests.post(url, headers=headers, params=payload)
    print(end_msg)




