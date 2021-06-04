# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 14:32:41 2021

@author: shen
"""


import datetime
import pandas as pd
import numpy as np
import pymssql
import os
#os.environ["GIT_PYTHON_REFRESH"] = "quiet"

product_list = ["ru","TA","MA","ZC","i","pp","l","v","pg","IF","cu","zn","al","au","SR","CF","RM","m","c"]
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  
start_date = datetime.datetime(2020, 6, 1)
all_data = {}
mean_hv = pd.Series()

for product in product_list:
    sql = "select Date,Ticker,HV from [Quant].[dbo].[HV_Daily] where Ticker='%s' and  Date>='%s' order by Date"%(product, start_date)
    temp_sql = pd.read_sql(sql, conn_ssql)
    all_data[product] = temp_sql



for product in product_list:
    table = all_data[product]
    #table.groupby(table['Date'].apply(lambda x :f"{x.year} - {x.month}")). mean()
    
    table['month'] = pd.to_datetime(table['Date']).dt.month
    table['year'] = pd.to_datetime(table['Date']).dt.year
    table['time'] = [0]*len(table)
    for i in range(len(table)):
        table['time'][i] = str(table['year'][i]) + '-' + str(table['month'][i])    
    temp_avg = table.groupby("time").mean()['HV']
    mean_hv = pd.concat([mean_hv,temp_avg],axis=1)

whole = mean_hv.iloc[:,1:]
whole.columns =product_list
path = 'Z:\SHEN'
os.chdir(path)
whole.to_excel("HV.xlsx")



