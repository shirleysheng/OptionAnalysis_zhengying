#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 17:55:56 2020

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



product_list = ['CU']
#RU
trading_day = 245   
bars_5m = 69
bars_30m = 12
start_date = datetime.datetime(2020, 1, 1)

conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")

class realized_vol:
    
    def __init__(self,df):
        self.df = df.copy()
        self.df.rename(columns={"time":"systemdate"}, inplace=True)  #systemdate 2020-02-24 09:05:00
        self.df["close_adj"] = self.df["close"] * self.df["multiplier"]  #multiplier 
        self.df["date"] = self.df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
        self.df["time"] = self.df["systemdate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
        self.df["minite"] = self.df["systemdate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    

    def get_5m_rv(self):
        self.df_5m = self.df[(self.df["time"]>"06:00:00") & (self.df["time"]<="23:00:00")].copy() #each 5 minutes
        self.df_5m["ret"] = np.log(self.df_5m["close_adj"]/self.df_5m["close_adj"].shift(1))
    
        self.date_set = np.sort(self.df_5m["date"].unique())
    
        rv5_5m = [0]*len(self.date_set)
        rv5_5m[0] = np.sqrt(np.square(self.df_5m[self.df_5m["date"].isin(self.date_set[-1:])]["ret"]).mean()*bars_5m*trading_day) #前一日5分钟rv
        
        for i in range(1,len(self.date_set)):
            rv5_5m[i] = np.sqrt(np.square(self.df_5m[self.df_5m["date"].isin(self.date_set[-(i+1):-i])]["ret"]).mean()*bars_5m*trading_day) 

        return rv5_5m
    
    def get_30m_rv(self):
        df_30m = self.df_5m[self.df_5m["minite"]%30==5].copy() 
        df_30m["ret"] = np.log(df_30m["close_adj"]/df_30m["close_adj"].shift(1))
        rv5_30m = np.sqrt(np.square(df_30m[df_30m["date"].isin(self.date_set[-5:])]["ret"]).mean()*bars_30m*trading_day)
        
        return rv5_30m
    
    def get_eod_rv(self):
        df_eod = self.df_5m[self.df_5m["time"]=="14:55:00"].copy()
        df_eod["ret"] = np.log(df_eod["close_adj"]/df_eod["close_adj"].shift(1))
        
        return df_eod
    
for product in product_list:
    sql = "select time,close,multiplier,instrumentid from futures_5m_continuing2 where productid='%s' and time>='%s' order by time"%(product, start_date)
    data = pd.read_sql(sql, conn)
    
rv =  realized_vol(data)
rv_5m = rv.get_5m_rv()
df_eod = rv.get_eod_rv()



# 1 day 5 minutes rv for 30 days
plt.figure()
plt.plot(np.arange(0,30,1),rv_5m[0:30])
plt.title('1 day 5 minutes rv for 30 days')
plt.xlabel("Day")
plt.ylabel("RV")
plt.show()


# 最大波动率
df_eod = df_eod.reset_index()
#每周波动
gap_day = 5
df_eod_week = df_eod.iloc[3::gap_day].copy()
df_eod_week['week_ret'] = np.log(df_eod_week["close_adj"]/df_eod_week["close_adj"].shift(1))

df_eod_week.head()

up_10 = df_eod_week.sort_values(by=['week_ret'],ascending=False).iloc[0:10,]
down_10 = df_eod_week.sort_values(by=['week_ret'],ascending=False).iloc[-10:,]

plt.figure()
plt.plot(np.arange(0,10,1),up_10['week_ret'])
plt.ylabel("Cu Ret")
plt.show()

plt.figure()
plt.plot(np.arange(0,10,1),down_10['week_ret'])
plt.ylabel("Cu Ret")
plt.show()

# every 1 months

df_eod['month'] = df_eod["date"].apply(lambda x:x.split("-")[1])


eod_1mon = [0]
monthly_date = [df_eod.iloc[1,]['date']]
for i in range(1,len(df_eod)):
    if df_eod['month'][i] != df_eod['month'][i-1]:
        eod_mon_temp = np.log(df_eod['close_adj'][i]/df_eod['close_adj'][i-1])
        monthly_date_temp = df_eod['date'][i]
        eod_1mon.append(eod_mon_temp)
        monthly_date.append(monthly_date_temp)
        
df_eod_mon = pd.DataFrame(list(zip(monthly_date, eod_1mon)), 
               columns =['date', 'monthly_return'])       
df_eod_mon = df_eod_mon.iloc[1:,]




#every 2 months 
gap_mon = 2 #every 2 months
#每周波动
df_eod_2mon = df_eod_mon.iloc[0::gap_mon] 

up_10_2mon = df_eod_2mon.sort_values(by=['return'],ascending=False).iloc[0:10,]
down_10_2mon = df_eod_2mon.sort_values(by=['return'],ascending=False).iloc[-10:,]




