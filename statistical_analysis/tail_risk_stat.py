#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 13:44:20 2020

@author: shensheng
"""
#计算每天1d 2d 3d 4d 最大涨跌幅      
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

trading_day = 252


product_list = ['PP']
#RU ZC TA
trading_day = 250
bars_5m = 69
start_date = datetime.datetime(2019, 1, 1)

conn = pymysql.connect("192.168.10.6", "cta-reader", "cta-reader","datacenter_futures")

for product in product_list:
    sql = "select time,close,multiplier,instrumentid from futures_5m_continuing2 where productid='%s' and time>='%s' order by time"%(product, start_date)
    data = pd.read_sql(sql, conn)



def processor_commo(df):
    df.rename(columns={"time":"systemdate"}, inplace=True)  #systemdate 2020-02-24 09:05:00
    df["close_adj"] = df["close"] * df["multiplier"]  #multiplier 
    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["time"] = df["systemdate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    df["minite"] = df["systemdate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df

data_pre = processor_commo(data)
#data_pre['5m_ret'] = np.log(data_pre["close_adj"]/data_pre["close_adj"].shift(1))



#close adj
#-------plot 价格走势图----

plt.figure()
plt.plot(data_pre['close_adj'])
plt.ylabel('price')
plt.show()

#------------------计算1d 2d ..4d最大波动
def get_eod(df):
   df_eod = df[df["time"]=="14:55:00"].copy()
   df_eod["1d_ret"] = np.log(df_eod["close_adj"]/df_eod["close_adj"].shift(1))
   
   return df_eod

df_eod = get_eod(data_pre)
df_eod = df_eod.reset_index(drop = True)


df_eod["2d_ret"] = df_eod["1d_ret"]+df_eod["1d_ret"].shift(1)
df_eod["3d_ret"] = df_eod["2d_ret"]+df_eod["1d_ret"].shift(2)
df_eod["4d_ret"] = df_eod["3d_ret"]+df_eod["1d_ret"].shift(3)



#1 2 3 4d 的return 涨幅 跌幅前10---------------------------------------------------------------

#只是按照1d的顺序排了 2d没有按照降序排列

up_1d = df_eod['1d_ret'].sort_values(ascending=False).iloc[:10,].reset_index(drop = True)
up_2d = df_eod['2d_ret'].sort_values(ascending=False).iloc[:10,].reset_index(drop = True)
up_3d = df_eod['3d_ret'].sort_values(ascending=False).iloc[:10,].reset_index(drop = True)
up_4d = df_eod['4d_ret'].sort_values(ascending=False).iloc[:10,].reset_index(drop  = True)
up_10 = pd.DataFrame({'1d_ret':up_1d,'2d_ret':up_2d, '3d_ret':up_3d, '4d_ret':up_4d} )


down_1d = df_eod['1d_ret'].sort_values().iloc[:10,].reset_index(drop = True)
down_2d = df_eod['2d_ret'].sort_values().iloc[:10,].reset_index(drop = True)
down_3d = df_eod['3d_ret'].sort_values().iloc[:10,].reset_index(drop = True)
down_4d = df_eod['4d_ret'].sort_values().iloc[:10,].reset_index(drop  = True)
down_10 = pd.DataFrame({'1d_ret':down_1d,'2d_ret':down_2d, '3d_ret':down_3d, '4d_ret':down_4d} )

up_10.to_excel("up_10.xls")
down_10.to_excel("down_10.xls")







#大跌之后的 二天的 max min avg -- ------- 涨跌幅
max_drop = df_eod[df_eod['1d_ret'] < -0.03]
#max_drop['date'] = pd.to_datetime(max_drop['date'])
max_drop_date = np.sort(max_drop['date'].unique())


max_drop_table = pd.DataFrame()


for date in max_drop_date:
    temp_index = df_eod[df_eod['date'] == date].index.values
    temp_table = df_eod.loc[temp_index+1,]
    max_drop_table = max_drop_table.append(temp_table)
    

np.max(max_drop_table['1d_ret']),np.min(max_drop_table['1d_ret']), np.mean(max_drop_table['1d_ret']) 
result = pd.DataFrame({'max':np.max(max_drop_table['1d_ret']),
                      'min':np.min(max_drop_table['1d_ret']), 
                      'avg':np.mean(max_drop_table['1d_ret'])},index=[0]) 


result.to_excel('drop.xls')


#hv 

def eod_hv(df):
    date_set = np.sort(df["date"].unique())
    #rv20_hv = [0]*len(date_set)
    df['20_hv'] = [0]* len(df)
    for i in range(len(date_set)-20):
        df['20_hv'].iloc[i+20] = np.sqrt(np.square(df[df["date"].isin(date_set[i:(i+20),])]["1d_ret"]).mean()*trading_day)
    
    return df

df_eod_hv = eod_hv(df_eod)



def eod_sigma(df):
    
    
    df['sigma'] = [0]* len(df)
    for i in range(len(df)):
        df['sigma'].iloc[i] = df["1d_ret"].iloc[i]/(df['20_hv'].iloc[i-1]/np.sqrt(252))

    return df


df_sigma = eod_sigma(df_eod_hv)

df_stat = df_sigma[['date','1d_ret','2d_ret','3d_ret','4d_ret','20_hv','sigma']]


def stat(df):
    avg = 
    







