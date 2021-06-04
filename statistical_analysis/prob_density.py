# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 10:00:53 2020

@author: shen
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
pd.set_option('display.float_format',lambda x : '%.3f' % x)#set_option 更改要显示的数据形式



conn=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  

sql_option = "select * from etf_510050_option_detail where monthIndex = 1 and \
((DATEPART(hour,Systemdate)*100 + DATEPART(minute,Systemdate) between 935 and 1125 \
or DATEPART(hour,Systemdate)*100 + DATEPART(minute,Systemdate) between 1305 and 1455)) \
and right(strikePrice,1)<>'A' order by Systemdate"  #

sql_future ="select * from etf_510050_option where monthIndex = 1 \
  and DATEPART(minute,Systemdate) %5 = 0 \
  and (skew <= 92 \
  or skew >=108) \
  order by systemDate"  #找skew 区间在92 - 108 
  
  
future_data_pre =  pd.read_sql(sql_future, conn)
option_data_pre = pd.read_sql(sql_option, conn)
# systemDate, underlyingPrice, monthSymbol



future_data = future_data_pre[['systemDate','monthSymbol','impv2']] 
option_data = option_data_pre[['systemDate','monthSymbol','forwardPrice','underlyingPrice','strikePrice','callMidPrice','putMidPrice','callImpv','putImpv','dueTime']]



result = pd.merge(future_data,option_data, on = ['systemDate','monthSymbol'])
result['strikePrice'] =  result['strikePrice'].astype(float)
#选择out of money:  #forward price 计算
result['moneyness'] = [0]* len(result)

for i in range(len(result)):
    if(result['forwardPrice'][i] < result['strikePrice'][i]):
        result['moneyness'][i] = 'call'
    else:
        result['moneyness'][i] = 'put'
        
        


    
#计算市场pdf
def prob_m(s0, k, i, t, iv):
    d1 = (np.log(s0/k) + (i + iv * iv /2) * t ) / iv/ np.sqrt(t)
    d2 = d1 - iv * np.sqrt(t)
    nd1 = norm.cdf(d1)
    nd2 = norm.cdf(d2)
    nd1d = np.exp(-1 * d1 * d1 /2) / np.sqrt(2 * np.pi)
    nd2d = np.exp( -1 * d2 * d2 /2) / np.sqrt(2 * np.pi)
    p_market = nd2d/k/iv/np.sqrt(t)     #*np.exp(-1*i*t) 求导有这一项 但ppt需要*e^rt
    
    
    return p_market
  


#计算理论pdf log normal
def prob_log(s0,sigma):
    p_log = (1/ (s0 * sigma * np.sqrt(2 * np.pi))) * np.exp(-1 * np.square(np.log(s0))/ (2 * np.square(sigma)))
    
    return p_log

  
result['prob_market'] = [0] * len(result)
for i in range(len(result)):
    if (result['moneyness'] == 'call'):
        result['prob_market']



#计算理论pdf log normal



































