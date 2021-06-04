#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 10:02:57 2020

@author: shensheng
"""

import pandas as pd
import numpy as np
import pymssql
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib as mpl

vix_raw = pd.read_csv("/Users/shensheng/Desktop/^VIX.csv")
sp_raw = pd.read_csv("/Users/shensheng/Desktop/^GSPC.csv")
# server    数据库服务器名称或IP
# user      用户名
# password  密码
# database  数据库名称

#Option..etf_510050_option


conn=pymssql.connect(host="192.168.10.6",user="hdr",password="gene@2019",database="Option")  
sql = "select systemDate, underlyingPrice,impv2, monthIndex from etf_510050_option"

#sql1 = "select top 5 * from etf_510050_option"
#temp_df = pd.read_sql(sql,conn)


full_df = pd.read_sql(sql,conn) #read data
df = full_df.copy() 

#df["time"] = df['systemDate'].to_pydatetime() 'Series' object has no attribute 'to_pydatetime'

df["systemDate"] = df['systemDate'].astype(str).tolist() 

#time = df["time"].str[-8:]  09:30:00... 取时间的另外一种方法

df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1]) #相当于 for 09:30:00
df["date"] = df["systemDate"].apply(lambda x:x.split(" ")[0]) # 2015-02-25

df_eod = df[df["time"]=='14:45:00' ].copy()
df_eod = df_eod[df_eod['monthIndex']==1]


#去除异常值
u = df_eod['impv2'].mean()  # 计算均值
std = df_eod['impv2'].std()  # 计算标准差

error = df_eod[np.abs(df_eod['impv2'] - u) > 3*std]  #异常值
data_c = df_eod[np.abs(df_eod['impv2'] - u) <= 3*std] #剔除异常值之后的数据

for i in range(len(df_eod)):
    if ((df_eod['impv2'].iloc[i] - u) > 3*std):
        df_eod['impv2'].iloc[i] = u   #均值替换

 
    
#2015- 2020 

# =============================================================================
# 
# fig = plt.figure(figsize=(15,5))
# 
# ax = plt.gca()
# ax.plot_date(xs, df_eod['underlyingPrice'], "-b",label="sp500")
# ax.plot(xs,df_eod['impv2'],"-r", label="impv2")
# ax.legend(loc="upper left")
# # 设置日期的显示格式
# date_format = mpl.dates.DateFormatter("%Y-%m-%d")
# ax.xaxis.set_major_formatter(date_format)
# 
# # 日期的排列根据图像的大小自适应
# fig.autofmt_xdate()
# 
# plt.show()
        
        
        
#a1.set_xticks(np.linspace(min(time), max(time), 1000))   
# =============================================================================



#2015-2020 plot 双y
fig = plt.figure(figsize=(10,5))
xs = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in df_eod['date']]
ax = fig.add_subplot(111)
ax.plot(xs,df_eod['impv2'],"-r", label = "impv2")

ax2 = ax.twinx()
ax2.plot(xs,df_eod['underlyingPrice'], '-b', label = "underlying")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
plt.title('underlying & impv2 from 2015 to 2020')
ax.set_xlabel("time")
ax.set_ylabel(r"impv2")
ax2.set_ylabel(r"underlying")



#underlying + impv2 for 2017
#提取2017年数据
df_2017 = df_eod.loc[(df_eod['date'] > '2017-01-01') & (df_eod['date'] < '2018-01-01')] 

xs_2017 = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in df_2017['date']]
#plt.plot(xs_2017,df_2017['impv2'],"-r", label="impv2")
    

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(xs_2017,df_2017['impv2'],"-r", label = "impv2")

ax2 = ax.twinx()
ax2.plot(xs_2017,df_2017['underlyingPrice'], '-b', label = "underlying")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
plt.title('underlying & impv2 for 2017')
ax.set_xlabel("time")
ax.set_ylabel(r"impv2")
ax2.set_ylabel(r"underlying")


#---------------------------------------------------------------------------------
#vix + sp500

#2015-2020
vix_year = [0]*len(vix_raw['Date'])

vix_raw["datetime"] = vix_raw['Date'].astype(str).tolist()
#vix_raw["datetime"] = vix_raw['Date'].apply(lambda x:x.split(" ")[1])

sp_raw["datetime"] = sp_raw['Date'].astype(str).tolist()



vix_con1 = (vix_raw['datetime'] > '2015-01-01') & (vix_raw['datetime'] <= '2020-12-21')
vix_2015 = vix_raw.loc[vix_con1]
sp_con1 = (sp_raw['datetime'] > '2015-01-01') & (sp_raw['datetime'] <= '2020-12-21')
sp_2015 = sp_raw.loc[sp_con1]

#vix + sp500 2015-2020 plot 双y
fig = plt.figure(figsize=(10,5))
xs_sp = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in sp_2015['datetime']]
ax = fig.add_subplot(111)
ax.plot(xs_sp,vix_2015['Adj Close'],"-r", label = "vix")

ax2 = ax.twinx()
ax2.plot(xs_sp,sp_2015['Adj Close'], '-b', label = "sp500")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
plt.title('vix & sp500 from 2015 to 2020')
ax.set_xlabel("time")
ax.set_ylabel(r"vix")
ax2.set_ylabel(r"sp500")

#max_vix = vix_2015[vix_2015['Adj Close'] ==max(vix_2015['Adj Close'])]


#2017
vix_con2 = (vix_raw['datetime'] > '2017-01-01') & (vix_raw['datetime'] < '2018-01-01')
vix_2017 = vix_raw.loc[vix_con2]
sp_con2 = (sp_raw['datetime'] > '2017-01-01') & (sp_raw['datetime'] < '2018-01-01')
sp_2017 = sp_raw.loc[sp_con2]


#vix + sp500 for 2017
fig = plt.figure(figsize=(10,5))
xs_sp2 = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in sp_2017['datetime']]
ax = fig.add_subplot(111)
ax.plot(xs_sp2,vix_2017['Adj Close'],"-r", label = "vix")

ax2 = ax.twinx()
ax2.plot(xs_sp2,sp_2017['Adj Close'], '-b', label = "sp500")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
plt.title('vix & sp500 for 2017')
ax.set_xlabel("time")
ax.set_ylabel(r"vix")
ax2.set_ylabel(r"sp500")




