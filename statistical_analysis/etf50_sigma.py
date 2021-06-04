     #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 10:23:25 2020

@author: shensheng
"""

import pandas as pd
import numpy as np
import pymssql
import datetime
import matplotlib.pyplot as plt

trading_day = 245

full_df = pd.read_csv('etf_510050_option.csv')

df = full_df[['systemDate', 'underlyingPrice','impv2', 'monthIndex','forwardPrice']]
df = df[df['monthIndex']==1]


df["systemDate"] = df['systemDate'].astype(str).tolist() 

df["date"] = df["systemDate"].apply(lambda x:x.split(" ")[0])
df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1])
df["minite"] = df["systemDate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))
df['year'] = df["date"].apply(lambda x:x.split("-")[0])

df_5m = df[(df["time"]>"09:35:00") & (df["time"]<="23:00:00")].copy() #去掉开盘第一个时刻
df_5m = df_5m[df_5m["minite"]%5==0].copy()

df_eod = df_5m[df_5m["time"]=="14:55:00"].copy()

#计算return 0945-1125-1500
df_5m = df_5m[df_5m['time'] != "11:30:00"] 
df_5m = df_5m[df_5m['time'] != "13:00:00"] #去掉中午休盘的两个时刻


#计算daily return
date_set = np.sort(df_5m["date"].unique())
day_ret = pd.DataFrame()
for day in date_set:
    temp = df_5m[df_5m['date'] == day]
    temp['ret'] = np.log(temp["underlyingPrice"]/temp["underlyingPrice"].shift(1))

    day_ret = day_ret.append(temp)

day_ret = day_ret.dropna()

#提取10个月
day_ret_10 = day_ret[day_ret['date']>"2020-02-21"]
day_ret_10 = day_ret_10.reset_index(drop = True)


up_s = day_ret_10[day_ret_10['ret'] >0]#找出>0的return 下一时刻的rv?
index_s = up_s.index.values +1
up_s1 = day_ret_10.iloc[index_s[:-1,], :]  #去掉了最后一个 上涨后下一时刻的return

#计算s1的vol

date_set = np.sort(up_s1["date"].unique())
bar_up = 48
up_rv =  [0]*len(date_set)
trading_day  = 252

#up_rv[0] = np.sqrt(np.square(up_s1[up_s1["date"].isin(date_set[-1:])]["ret"]).mean()*bar_up*trading_day) #一日5分钟rv
up_rv[0] = np.std(up_s1[up_s1["date"].isin(date_set[-1:])]["ret"]) * np.sqrt(trading_day* bar_up)

for i in range(1,len(date_set)):
    up_rv[i] = np.std(up_s1[up_s1["date"].isin(date_set[-(i+1):-i])]["ret"]) * np.sqrt(trading_day* bar_up) 


up_tuples = list(zip(date_set[::-1], up_rv))  
up_vol = pd.DataFrame(up_tuples, 
                  columns = ['Date', 'vol_up']) 
 




#找出<0的return 下一日的rv?
down_s = day_ret_10[day_ret_10['ret'] <0]
index_d = down_s.index.values +1
down_s1 = day_ret_10.iloc[index_d[:-1,], :] 

date_set_down = np.sort(down_s1["date"].unique())
down_rv =  [0]*len(date_set_down)

down_rv[0] = np.std(down_s1[down_s1["date"].isin(date_set_down[-1:])]["ret"]) * np.sqrt(trading_day* bar_up)


for i in range(1,len(date_set_down)):
    down_rv[i] = np.std(down_s1[down_s1["date"].isin(date_set[-(i+1):-i])]["ret"]) * np.sqrt(trading_day* bar_up) 


down_tuples = list(zip(date_set_down[::-1], down_rv))  
down_vol = pd.DataFrame(down_tuples, 
                  columns = ['Date', 'vol_down']) 


result = pd.merge(up_vol,down_vol, on='Date')
xs = [datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in result['Date']]

# =============================================================================
# plt.figure()
# plt.plot(xs,result['vol_up'],"-r", label = "up")
# plt.plot(xs,result['vol_down'],"-b", label = "down")
# plt.ylabel("vol")
# plt.legend(loc="upper left")
# 
# plt.show()
# =============================================================================

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(xs,result['vol_up'],"-r", label = "up")
ax.plot(xs,result['vol_down'], '-b', label = "down")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)

#2020-03-13
t = down_s1[down_s1['date'] =='2020-03-13']


fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.plot(up_s['underlyingPrice'],"-r", label = "up")
ax.plot(down_s['underlyingPrice'], '-b', label = "down")
fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)


plt.plot(up_s['ret'].iloc[0:50,])
