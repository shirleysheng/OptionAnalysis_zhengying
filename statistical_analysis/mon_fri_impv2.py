# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 09:37:06 2021

@author: shen
"""


import pandas as pd
import numpy as np
import pymssql
import datetime
import matplotlib.pyplot as plt




start_date = datetime.datetime(2020, 1, 1)

conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  

sql_ssql = "select systemDate, monthSymbol, impv2, monthIndex from  etf_510050_option where systemDate>='%s' and monthIndex = 0 order by systemDate"%(start_date) #

ssql_pre = pd.read_sql(sql_ssql, conn_ssql)


def processor_etf(df):
    df["systemDate"] = df['systemDate'].astype(str).tolist()
    df.rename(columns={"time":"systemDate"}, inplace=True)  #systemdate 2020-02-24 09:05:00    df["date"] = df["systemdate"].apply(lambda x:x.split(" ")[0]) #date 2020-02-24
    df["date"] = df["systemDate"].apply(lambda x:x.split(" ")[0]) #time 09:05:00 09:10:00  
    df["time"] = df["systemDate"].apply(lambda x:x.split(" ")[1]) #time 09:05:00 09:10:00
    #df["minite"] = df["systemDate"].apply(lambda x:int(x.split(" ")[1].split(":")[1]))#5 10 15...
    return df

etf_ssql = processor_etf(ssql_pre)

etf_eod = etf_ssql[etf_ssql['time'] == '14:45:00'].copy().reset_index(drop = True)
#etf_eod['Date'] = pd.to_datetime(etf_eod['Date'])

col2 = 'impv2'

etf_group = etf_eod.groupby('monthSymbol').apply(lambda x: (x[col2] - x[col2].shift(1)))

etf_eod['impv_diff'] = etf_group.values
etf_eod['week_day'] = pd.to_datetime(etf_eod['date']).apply(lambda x:x.weekday())

etf_fri = etf_eod[etf_eod['week_day'] == 4]

etf_fri_mon = etf_eod.query('week_day == 4 | week_day == 0')

etf_mon_group = etf_fri_mon.groupby('monthSymbol').apply(lambda x: (x[col2].shift(1) - x[col2]))



etf_fri_mon['mon_fri'] = etf_mon_group.values

etf_mon = etf_fri_mon[etf_fri_mon['week_day'] == 4].dropna()

plt.plot(etf_fri['impv_diff'])
etf_fri.to_excel('fri_thur.xls')
etf_mon.to_excel('mon_fri.xls')


