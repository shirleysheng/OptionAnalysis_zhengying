# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 14:16:27 2021

@author: shen
"""

import pandas as pd
import numpy as np
import pymssql
import datetime
import matplotlib.pyplot as plt



trading_day = 245

us_data = pd.read_excel('us_curve.xlsx')
us_10y = us_data[['Date','10 Yr']]
us_date = pd.to_datetime(us_10y['Date']).astype(str)

us_d = [datetime.datetime.strptime(d, '%Y-%m-%Y') for d in us_date]

us_10y['date'] = us_date



start_date = datetime.datetime(2001, 1, 1)

conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  

sql_ssql = "select systemDate, monthSymbol, underlyingPrice, monthIndex from  etf_510050_option where systemDate>='%s' order by systemDate"%(start_date) #

ssql_pre = pd.read_sql(sql_ssql, conn_ssql)
ssql = ssql_pre[ssql_pre['monthIndex'] ==1 ]

def processor_etf(df):
    df["systemDate"] = df['systemDate'].astype(str).tolist()
    df.rename(columns={"time":"systemDate"}, inplace=True)  #systemdate 2020-02-24 09:05:00    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["date"] = df["systemDate"].apply(lambda x:x.split(" ")[0]) #time 09:05:00 09:10:00  
    df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    #df["minite"] = df["systemDate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df

etf_ssql = processor_etf(ssql)

etf_eod = etf_ssql[etf_ssql['time'] == '14:55:00'].copy()
#etf_eod['Date'] = pd.to_datetime(etf_eod['Date'])

result = pd.merge(etf_ssql,us_10y, on = ['date'])



plt.figure()
plt.plot(result['underlyingPrice'],"-r", label = "etf50")
plt.plot(result['10 Yr'],"-b", label = "us_curve")
plt.legend(loc="upper left")

plt.show()



# =============================================================================
# plt.figure(figsize=(20,5))
# plt.plot(xs, result['underlyingPrice'], "-r",label = "etf50" )
# plt.xticks(xs[::1200], rotation=90 , fontsize=14)
# plt.show()
# =============================================================================

import matplotlib.ticker as ticker  #调整x轴坐标显示问题
xs = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in result['date']]   
fig1 = plt.figure(figsize=(10,5))
ax = fig1.add_subplot(111)
ax.plot(xs, result['underlyingPrice'], "-r",label = "etf50" )
ax.plot(xs,result['10 Yr'],"-b", label = "us_curve")
tick_spacing = 20  #显示密度
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
plt.xticks(rotation=45)
fig1.legend(loc=2, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)



