# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 13:47:26 2021

@author: shen
"""

import datetime
from datetime import timedelta
import pandas as pd
import numpy as np
import pymysql
import pymssql
import os
import time
import matplotlib.pyplot as plt
os.chdir(r"Z:\SHEN\CostMargin")
from margin import calculate_margin, get_marginfactor
pd.set_option('display.float_format',lambda x : '%.3f' % x)
from matplotlib.backends.backend_pdf import PdfPages
pd.set_option('mode.chained_assignment', None)

#
product_list = ['PG','V','M','PP','L','I','C']#  
#郑商所：'MA','TA','ZC','CF','SR','RM'     大连交易所：'PG','V','M','PP','L','I','C' 上交所： 'AU','CU','ZN','AL','RU'
conn_ssql=pymssql.connect(host="192.168.10.6",user="shengshen",password="shengshen",database="Option")  
Tlist = {}
#minivlist = {}
targetsimga = 2
minsigma = 1.5
profit_C_list = {}
profit_P_list = {}
profit_P_adj_list = {}
profit_C_adj_list = {}

os.chdir(r"C:\Users\shen\Desktop")
with PdfPages('Curvebyproduct_comm.pdf') as pdf:
    for product in product_list:
        print(product)
        today = datetime.datetime.today()
        now = (today.replace(today.year,today.month,today.day,21,0,0,0)).strftime('%Y-%m-%d %H:%M:%S')
        #找到距离目前最近的上一时刻
        sql_lasttime = "Select TOP 1 systemDate from %s_future_option_detail " \
                    "where SystemDate<='%s' " \
                    "and (datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 905 and 1010 "\
                    "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 1035 and 1125 " \
                    "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 1335 and 1455 " \
                    "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate)<100 " \
                    "or datepart(hour,Systemdate)*100+datepart(minute,Systemdate) between 2105 and 2255) order by SystemDate desc"%(product,now) # and halfSpreadIndex is not NULL 流动性指标
        lasttime = pd.read_sql(sql_lasttime, conn_ssql)
        start_date = lasttime['systemDate'][0].date() -timedelta(60)
        marginfactor = get_marginfactor(product)
        size = marginfactor[2]
        commission = marginfactor[3]
        #load HV iv
        sql = "Select Date,C,IMPV2,T,HV " \
            "from (Select a.Date,a.C,b.IMPV2,b.monthDueTime*250 as T,c.HV as HV,expid=dense_rank()" \
            "over(partition by b.SystemDate order by b.monthDueTime)" \
            "from Quant..OHLC_Daily a inner join[Option]..[%s_future_option] b " \
            "on a.Date=cast(b.SystemDate as Date) inner join Quant..HV_Daily c on a.Date=c.Date and a.Ticker=c.Ticker " \
            "where a.Date>='%s' and datepart(hour,b.SystemDate)*100+datepart(minute,b.SystemDate)=1455" \
            "and b.monthDueTime*250>=3 and a.Ticker='%s') x " \
            "where x.expid=1 order by Date" %(product, start_date,product)
        data = pd.read_sql(sql,conn_ssql)  #pd.to_datetime
        #plot CLOSE HV IMPV FOR EACH COMMODITY
        fig = plt.figure(figsize=(12,6))
        xs = data['Date']
        ax = fig.add_subplot(111)
        ax.plot(xs,data['IMPV2'],"-r", label = "impv2")
        ax.plot(xs,data['HV'],"-b", label = "hv")
    
        ax2 = ax.twinx()
        ax2.plot(xs,data['C'], '-k', label = "close")
        fig.legend(loc=3, bbox_to_anchor=(1,1), bbox_transform=ax.transAxes)
        plt.title(f'{product}_{lasttime["systemDate"][0]}_IMPV2: {round(np.mean(data["IMPV2"]),2)}_HV: {round(np.mean(data["HV"]),2)} ')
        ax.set_xlabel("date")
        ax.set_ylabel(r"impv2")
        ax2.set_ylabel(r"close")
        plt.show()
        pdf.savefig(fig)
        plt.close(fig)
    
        #load opt curve
        sql_opt = "Select dueTime*250 as T, StrikePrice as K, forwardprice as F , UnderlyingPrice as S," \
                "(case when StrikePrice>=forwardprice then callmidprice else putmidprice end) as Optprice," \
                "(case when StrikePrice>=forwardprice then callImpv else putImpv end) as OTMIV " \
                " FROM [Option]..[%s_future_option_detail] WHERE SystemDate='%s' " \
                "and (case when StrikePrice>=forwardprice then callAskPrice1-CallBidPrice1 else PutAskPrice1-PutBidPrice1 end)<=20" \
                " order by dueTime,StrikePrice" %(product,lasttime['systemDate'][0])
        opt_data = pd.read_sql(sql_opt,conn_ssql)#得到的是一个品种下 目前时刻所有合约数据
        firstT = np.sort(opt_data['T'].unique())[0]#取最近的合约
        Tlist[product] = firstT
        opt_nearby = opt_data[opt_data['T'] == firstT]#取最近合约的数据
        opt_nearby.loc[:,'K'] = opt_nearby['K'].astype(float)
        opt_nearby = opt_nearby.sort_values(by="K") #按照K降序排序
        minprice = np.min(opt_nearby['Optprice'])#取最小price
        putdata = opt_nearby[opt_nearby['K']< opt_nearby['F']].reset_index(drop = True)#将数据分开成call put的虚值数据
        calldata = opt_nearby[opt_nearby['K'] > opt_nearby['F']].reset_index(drop = True)
        #分别遍历call put数据，去除错误数据
        used_p = 1
        if(len(putdata) > 2):
            for i in range(1,len(putdata))[::-1]:
                if(putdata['Optprice'][i]<putdata['Optprice'][i-1]):
                    used_p = i
                    break
        used_c = len(calldata)
        if(len(calldata) > 2):
            for i in range(len(calldata)-1):
                if(calldata['Optprice'].iloc[i] < calldata['Optprice'].iloc[i+1]):
                    used_c = i 
                    break
                
        putdata_f = putdata.iloc[used_p:]
        putdata_f = putdata_f[putdata_f['Optprice']>minprice]
        calldata_f = calldata.iloc[:used_c]
        calldata_f = calldata_f[calldata_f['Optprice']>minprice]
        
        whole_data = putdata_f.append(calldata_f)
        whole_data = whole_data[whole_data['OTMIV'] > 0]
        
        #流动性差导致 数据空白 error
        if whole_data.empty == True:
            print(f"{product}流动性差")
            continue
        else:
            
            sigmalist = np.log(whole_data['K']/whole_data['F']) / (whole_data['OTMIV'] / np.sqrt(250) *np.sqrt(whole_data['T']))#计算sigma
            ATMIV = float(np.array(whole_data['OTMIV'])[np.where(abs(sigmalist)== min(abs(sigmalist)))])
            
            matchp = np.where(abs(sigmalist + targetsimga) == min(abs(sigmalist + targetsimga))) #离targetsigma最近的位置的put
            matchc = np.where(abs(sigmalist - targetsimga) == min(abs(sigmalist - targetsimga)))
        
            IV_P = float(np.array(whole_data['OTMIV'])[matchp])
            IV_C = float(np.array(whole_data['OTMIV'])[matchc])
            K_P = float(np.array(whole_data['K'])[matchp])
            K_C = float(np.array(whole_data['K'])[matchc])
            price_p = float(np.array(whole_data['Optprice'])[matchp])
            price_c = float(np.array(whole_data['Optprice'])[matchc])
            minprice = min(whole_data['Optprice'])
            minIV = min(whole_data['OTMIV'])  #可删
            maxIV = max(whole_data['OTMIV'])
            S = whole_data['S'].iloc[0]
            T = whole_data['T'].iloc[0]
            
            sigma_p = np.array(sigmalist)[matchp][0]
            sigma_c = np.array(sigmalist)[matchc][0]
        
            margin_P = round(calculate_margin(product,S,K_P,2,price_p),0)
            margin_C = round(calculate_margin(product,S,K_C,1,price_c),0)
            profit_P = 1/margin_P*(price_p*size-commission)/((T+1)/250)
            profit_C = 1/margin_C*(price_c*size-commission)/((T+1)/250)
            
            lever_P = 1/margin_P*S*size     
            lever_C = 1/margin_C*S*size
            profit_P_adj = profit_P/lever_P*10
            profit_C_adj = profit_C/lever_C*10   #profit_adj ??? *10?
        
        #plot sigma of option chain for every single commo
            fig2 = plt.figure()
            plt.plot(sigmalist,whole_data['OTMIV'],linestyle='-',marker='o',markerfacecolor = 'red')
            plt.xlabel('sigma')
            plt.ylabel('IV')
            plt.title(f'{product}_{whole_data["K"].iloc[0]}~{whole_data["K"].iloc[-1]}({S}) ATM:{round(ATMIV *100,2)}, P{round(IV_P *100,2)} ({round(IV_P/ATMIV,2)})'  
                      f' C{round(IV_C*100,2)} ({round(IV_C/ATMIV,2)})')
            plt.axvline(sigma_c,c="red",label=f'{K_C} IV:{IV_C} price:{price_c} lev: sig:{round(sigma_c,2)}')
            plt.axvline(sigma_p,c="green", label=f'{K_P} IV:{IV_P} price:{price_p} lev: sig:{round(sigma_p,2)}')
        
            plt.legend()
            plt.show()
            pdf.savefig(fig2)
            plt.close(fig2)
            
            #计算MARGIN PROFIT
            profit_P_list[product] = profit_P if abs(sigma_p) >= minsigma else 0
            profit_C_list[product] = profit_C if abs(sigma_c) >= minsigma else 0
            profit_P_adj_list[product] = profit_P_adj if abs(sigma_p) >= minsigma else 0
            profit_C_adj_list[product] = profit_C_adj if abs(sigma_c) >= minsigma else 0
        
    #plot annual profit for all commo 
    fig3 = plt.figure(figsize=(8,5))
    plt.scatter(profit_P_list.values(), profit_P_adj_list.values(),color='green')
    for i in range(len(profit_P_list)):
        plt.annotate(list(profit_P_list.keys())[i], xy = (list(profit_P_list.values())[i], list(profit_P_adj_list.values())[i]), 
                     xytext = (list(profit_P_list.values())[i]+0.001, list(profit_P_adj_list.values())[i]+0.001))
    plt.xlabel("annual profit")
    plt.ylabel("annual profit adjust")
    plt.title(f"IV:{lasttime['systemDate'][0]}, red is call, green is put")
    plt.scatter(profit_C_list.values(), profit_C_adj_list.values(),color='red')
    for i in range(len(profit_C_list)):
        plt.annotate(list(profit_C_list.keys())[i], xy = (list(profit_C_list.values())[i], list(profit_C_adj_list.values())[i]), 
                     xytext = (list(profit_C_list.values())[i]+0.001, list(profit_C_adj_list.values())[i]+0.001))
    plt.show()
    pdf.savefig(fig3)
    plt.close(fig3)
    


