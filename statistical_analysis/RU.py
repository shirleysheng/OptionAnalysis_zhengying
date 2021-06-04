#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 10:03:08 2020

@author: shensheng
"""

import datetime
import pandas as pd
import numpy as np
import pymysql
import pymssql
import os
import time
import statsmodels.api as sm
from scipy.stats import norm
import matplotlib.pyplot as plt
pd.set_option('display.float_format',lambda x : '%.3f' % x)



product_list = ["MA"]
trading_day = 245   
bars_5m = 69
bars_30m = 12
start_date = start_date = datetime.datetime(2000, 1, 1)

conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")


for product in product_list:
    sql = "select time,close,multiplier,instrumentid from futures_5m_continuing2 where productid='%s' and time>='%s' order by time"%(product, start_date)
    df = pd.read_sql(sql, conn)
    df.rename(columns={"time":"systemdate"}, inplace=True)  #systemdate 2020-02-24 09:05:00
   #prodoct = {ele : pd.DataFrame() for product in product_list}
    
    df["close_adj"] = df["close"] * df["multiplier"]  #multiplier 
    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["time"] = df["systemdate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    df["minite"] = df["systemdate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...

    df_5m = df[(df["time"]>"06:00:00") & (df["time"]<="23:00:00")].copy() #each 5 minutes
    df_30m = df_5m[df_5m["minite"]%30==5].copy()  #each 30 minutes
    #df_gap = df_5m[df_5m["minite"]%gap==5].copy() #each gap minutes
    
    
    df_eod = df_5m[df_5m["time"]=="14:55:00"].copy() # close time for each day
    
    df_5m["ret"] = np.log(df_5m["close_adj"]/df_5m["close_adj"].shift(1))
    df_30m["ret"] = np.log(df_30m["close_adj"]/df_30m["close_adj"].shift(1))
    df_eod["daily_ret"] = np.log(df_eod["close_adj"]/df_eod["close_adj"].shift(1))
    
    date_set = np.sort(df_5m["date"].unique())
    
    rv5_5m = [0]*len(date_set)
    rv5_5m[0] = np.sqrt(np.square(df_5m[df_5m["date"].isin(date_set[-1:])]["ret"]).mean()*bars_5m*trading_day) #前一日5分钟rv
    
    for i in range(1,len(date_set)):
        rv5_5m[i] = np.sqrt(np.square(df_5m[df_5m["date"].isin(date_set[-(i+1):-i])]["ret"]).mean()*bars_5m*trading_day) 



#每周波动
gap_day = 5
df_eod_week = df_eod.iloc[3::gap_day].copy()
df_eod_week['week_ret'] = np.log(df_eod_week["close_adj"]/df_eod_week["close_adj"].shift(1))




up_10 = df_eod_week.sort_values(by=['week_ret'],ascending=False).iloc[0:10,]
down_10 = df_eod_week.sort_values(by=['week_ret'],ascending=False).iloc[-10:,]

print(up_10)


plt.figure()
plt.plot(df_eod['daily_ret'])
plt.ylabel("Ru Ret")
plt.show()

plt.figure()
plt.plot(rv5_5m)
plt.ylabel("Ru Ret")
plt.show()

