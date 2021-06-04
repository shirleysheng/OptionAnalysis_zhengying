#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 00:22:51 2021

@author: shensheng
"""

from bs4 import BeautifulSoup
import urllib
import requests
import pandas as pd
import os
import re
# =============================================================================
# browser = webdriver.Chrome()
# browser.get('http://www.baidu.com/')
# 
# 
# from selenium import webdriver
# browser = webdriver.Chrome()
# 
# chromedriver_path = '/usr/local/bin/chromedriver
# 
# driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
# =============================================================================


trade_date = pd.read_csv("C:/Users/shen/Desktop/data/trade_days_13.csv") 

date_18 = pd.to_datetime(trade_date['DateTime']).dt.date
date1 = date_18[53:]

date2 = date_18[13:53]
date3 = date_18[4:12]
date4 = date_18[:4]

user_agent = "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
headers = {'User-Agent': user_agent}
df_data = pd.DataFrame()
date_list = []
for date in date3:
    try:
        print(date)
        url = f"https://www.cngold.org/yehq/{date}/list_history_109_1.html"
        request = urllib.request.Request(url,headers=headers)
        res = urllib.request.urlopen(request)
        soup = BeautifulSoup(res)
        num = soup.find_all('a',text = re.compile("[\u4e00-\u9fa5]+考价格$"))
        for link in num:
            url_new = link.get('href')
        
        #one = soup.find_all('div', class_="left_info")
        #finditem = re.compile(r'<a href="(.*?)">')
        
        
        request_new = urllib.request.Request(url_new,headers=headers)
        res_new = urllib.request.urlopen(request_new)
        soup_new = BeautifulSoup(res_new)
        num_new = soup_new.find_all("table",limit = 1)
    
        for item in num_new:
            t = item.find_all("td")
    
        value_res = []
        for i in range(len(t)):
                #temp_data = t[i].string.replace("\n", "")

            temp_data = t[i].text.replace("\n", "")
            value_res.append(temp_data)
    
        df_list = [value_res[i:i+7] for i in range(7,len(value_res),7)] # df_list = [value_res[i:i+7] for i in range(0,len(value_res),7)]
        df_temp = pd.DataFrame(df_list)
        date_list = [date] * len(df_list)
        df_temp['date'] = date_list
        df_data = df_data.append(df_temp)
    except:
        pass
    continue


df_data.columns = ['单品','生产厂家','种类','地域','价格(元/吨)','报价日期','日期']
df1 = df_data.copy()
df3 = df_data[df_data['报价日期'] > '2013-03-08'].copy()
df2 = df_data[df_data['报价日期'] <= '2013-03-08'].copy()
df2 = df2.append(df_data)
df_data.to_csv('14_16_pg_price.csv')
data = pd.read_csv('14_16_pg_price.csv',index_col=[0])
# =============================================================================
# data = pd.read_csv("C:/Users/shen/Desktop/18pg_price.csv")
# data = data.iloc[:,1:]
# t = data[data['日期'] > "2020-04-01"].drop(6169)
# 
# er  = data[data['产品价格'] >10000]
# 
# =============================================================================
