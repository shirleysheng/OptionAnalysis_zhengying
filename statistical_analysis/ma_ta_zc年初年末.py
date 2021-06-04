#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 09:13:46 2020

@author: shensheng
"""
#--------------------计算每年前一周和 后一周的return --------------------------
import datetime
import pandas as pd
import numpy as np
import pymysql
import pymssql
import os
import time
from scipy.stats import norm
import matplotlib.pyplot as plt
pd.set_option('display.float_format',lambda x : '%.3f' % x)


def processor(df):
    df.rename(columns={"time":"systemdate"}, inplace=True)  #systemdate 2020-02-24 09:05:00
    df["close_adj"] = df["close"] * df["multiplier"]  #multiplier 
    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["time"] = df["systemdate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    df["minite"] = df["systemdate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df

def end_of_day(df):
    df_5m = df[(df["time"]>"09:35:00") & (df["time"]<="23:00:00")].copy() #去掉开盘第一个时刻
    df_5m = df_5m[df_5m["minite"]%5==0].copy()

    df_eod = df_5m[df_5m["time"]=="14:55:00"].copy()
    df_eod['year'] = df_eod["date"].apply(lambda x:x.split("-")[0])

    return df_eod

#--------------------------------------商品名称--------------------
product_list = ['MA','TA','ZC']
#ZC TA
start_date = datetime.datetime(2015, 1, 1)

conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")

list_of_dfs = {}

for product in product_list:
    sql = "select time,close,multiplier,instrumentid from futures_5m_continuing2 where productid='%s' and time>='%s' order by time"%(product, start_date)
    #data = pd.read_sql(sql, conn)
    list_of_dfs[product] = pd.read_sql(sql, conn)



ma_data = list_of_dfs['MA']
ta_data = list_of_dfs['TA']
zc_data = list_of_dfs["ZC"]

data_pre = processor(ma_data.copy()) #修改这里 为其他商品数据
df_eod = end_of_day(data_pre) 
df_eod = df_eod.reset_index(drop = True)
year = np.sort(df_eod["year"].unique())  


whole = pd.DataFrame()
before_high = [0]*len(year)
before_low = [0] * len(year)
before = [0] * len(year)
a_high = [0]*len(year)
a_low = [0] * len(year)
a = [0] * len(year)

for i in range(len(year)):
    temp_bef = df_eod[df_eod["year"] == year[i]].iloc[0:5,]
    temp_index = df_eod[df_eod.index == temp_bef.index[0]-1]
    temp_before = temp_index.append(temp_bef)
    temp_after = df_eod[df_eod["year"] == year[i]].iloc[-6:,]
        
    #caculate return before
    temp_before['ret'] = np.log(temp_before["close_adj"]/temp_before["close_adj"].shift(1))
    before_max = np.log(np.max(temp_before['close_adj'].iloc[1:,])/temp_before['close_adj'].iloc[0])
    before_min = np.log(np.min(temp_before['close_adj'].iloc[1:,])/temp_before['close_adj'].iloc[0])
    before_sum = np.sum(temp_before['ret'])
    
    
    before_high[i]= before_max
    before_low[i] = before_min
    before[i] = before_sum
    
    temp_after['ret'] = np.log(temp_after["close_adj"]/temp_after["close_adj"].shift(1))
    a_max = np.log(np.max(temp_after['close_adj'].iloc[1:,])/temp_after['close_adj'].iloc[0])
    a_min = np.log(np.min(temp_after['close_adj'].iloc[1:,])/temp_after['close_adj'].iloc[0])
    a_sum = np.sum(temp_after['ret'])
    
    a_high[i]= a_max
    a_low[i] = a_min
    a[i] = a_sum
    
    t = [temp_before,temp_after]
    temp = pd.concat(t)
    whole = whole.append(temp)
    
    

# =============================================================================
# whole['daily_ret'] = np.log(whole['close_adj']/whole['close_adj'].shift(1))
# 
# whole.to_excel('ma_whole.xls')  
# =============================================================================


tuples = list(zip(year, before,before_high,before_low,a,a_high,a_low))
product = pd.DataFrame(tuples, 
                  columns = ['Date', 'year_start','start_high','start_low','year_end','end_high','end_low']) 
 
product.to_excel('ma.xls')    




#-----------------------------etf
def processor_etf(df):
    df["systemDate"] = df['systemDate'].astype(str).tolist() 

    df["date"] = df["systemDate"].apply(lambda x:x.split(" ")[0])
    df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1])
    df["minite"] = df["systemDate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))
    df['year'] = df["date"].apply(lambda x:x.split("-")[0])
    
    return df

def end_of_day(df):
    df_5m = df[(df["time"]>"09:35:00") & (df["time"]<="23:00:00")].copy() #去掉开盘第一个时刻
    df_5m = df_5m[df_5m["minite"]%5==0].copy()

    df_eod = df_5m[df_5m["time"]=="14:55:00"].copy()
    df_eod['year'] = df_eod["date"].apply(lambda x:x.split("-")[0])

    return df_eod


conn_etf=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  
#sql = "select systemDate, underlyingPrice,impv2, monthIndex,from etf_510050_option"


sql_etf = "select * from etf_510050_option where monthIndex =1 and  systemDate >='%s' order by systemDate"%(start_date)

etf_data = pd.read_sql(sql_etf, conn_etf)

df_etf = etf_data[['systemDate', 'underlyingPrice','impv2', 'monthIndex','forwardPrice']]
data_pre = processor_etf(df_etf.copy()) #修改这里 为其他商品数据

df_eod = end_of_day(data_pre) 
df_eod = df_eod.reset_index(drop = True)
year = np.sort(df_eod["year"].unique())  


whole = pd.DataFrame()
before_high = [0]*len(year)
before_low = [0] * len(year)
before = [0] * len(year)
a_high = [0]*len(year)
a_low = [0] * len(year)
a = [0] * len(year)

for i in range(len(year)):
    temp_bef = df_eod[df_eod["year"] == year[i]].iloc[0:5,]
    temp_index = df_eod[df_eod.index == temp_bef.index[0]-1]
    temp_before = temp_index.append(temp_bef)
    temp_after = df_eod[df_eod["year"] == year[i]].iloc[-6:,]
        
    #caculate return before
    temp_before['ret'] = np.log(temp_before["close_adj"]/temp_before["close_adj"].shift(1))
    before_max = np.log(np.max(temp_before['close_adj'].iloc[1:,])/temp_before['close_adj'].iloc[0])
    before_min = np.log(np.min(temp_before['close_adj'].iloc[1:,])/temp_before['close_adj'].iloc[0])
    before_sum = np.sum(temp_before['ret'])
    
    
    before_high[i]= before_max
    before_low[i] = before_min
    before[i] = before_sum
    
    temp_after['ret'] = np.log(temp_after["close_adj"]/temp_after["close_adj"].shift(1))
    a_max = np.log(np.max(temp_after['close_adj'].iloc[1:,])/temp_after['close_adj'].iloc[0])
    a_min = np.log(np.min(temp_after['close_adj'].iloc[1:,])/temp_after['close_adj'].iloc[0])
    a_sum = np.sum(temp_after['ret'])
    
    a_high[i]= a_max
    a_low[i] = a_min
    a[i] = a_sum
    
    t = [temp_before,temp_after]
    temp = pd.concat(t)
    whole = whole.append(temp)
    
    



