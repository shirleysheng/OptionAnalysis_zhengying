# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 09:54:13 2021

@author: shen
"""
import numpy as np
import pandas as pd

def get_marginfactor(product):

    data = pd.read_excel(r'Z:\SHEN\CostMargin\Record\margin_summary.xlsx')

    sizelist = data.groupby('Product')['Size'].apply(float).to_dict()
    margin_ratio1 = data.groupby('Product')['ratio'].apply(float).to_dict()
    margin_ratio2 = data.groupby('Product')['ratio2'].apply(float).to_dict()
    
    factor1 = margin_ratio1[product]
    factor2 = margin_ratio2[product]
    size = sizelist[product]
    productlist = ["M","I","RU","C","SR",
    "CF","CU","TA","MA","AU",
     "RM","PG","ZC","PP","V",
     "L","AL","ZN","IO","300","50"]
    commissionlist = [1.01,2.01,3.01,0,1.51,
     1.53,5.1,0.51,0.51,2.04,
     0.81,1.01,1.51,0.51,0.51,
     0.51,1.53,1.53,15.01,1.9,1.9]
    matchid = np.where(np.array(productlist) == product)[0]
    commission = float(np.array(commissionlist)[matchid]) 
    return(factor1,factor2,size, commission)


# =============================================================================
# #caculate margin
# def calculate(product,S,K,PC,optprice):
#     marginfactor = get_marginfactor(product)
#     factor1 = marginfactor[0]
#     factor2 = marginfactor[1]
#     size = marginfactor[2]
#     OTMvalue = max((K-S if PC==1 else S-K),0) * size
#     
#     if (product == "50" or product == "300"):
#         margin = (optprice+ max((factor1*S - max(K-S,0)),factor2*S ))*size if PC ==1 else \
#             min(optprice + max((factor1 * S - max(S-K, 0)), factor2 * K),K)*size
#     else:
#         margin = max(optprice*size+S*size*factor1-OTMvalue*factor2, optprice*size+S*size*factor1/2)
#     return margin
# =============================================================================


def calculate_margin(product,S,K,PC,optprice):
    marginfactor = get_marginfactor(product)
    factor1 = marginfactor[0]
    factor2 = marginfactor[1]
    size = marginfactor[2]
    OTMvalue = max((K-S if PC==1 else S-K),0) * size
    
    if (product == "50" or product == "300"):
        margin = (optprice+ max((factor1*S - max(K-S,0)),factor2*S ))*size if PC ==1 else \
            min(optprice + max((factor1 * S - max(S-K, 0)), factor2 * K),K)*size
    else:
        margin = max(optprice*size+S*size*factor1-OTMvalue*factor2, optprice*size+size*factor1*0.5*(K if product == 'IO' and PC !=1 else S))
    return margin



# =============================================================================
# 
# def get_marginfactor(product):
#     productlist = ["M","I","RU","C","SR",
#     "CF","CU","TA","MA","AU",
#     "RM","PG","ZC","PP","V",
#     "L","AL","ZN","IO","300","50"]
#     
#     marginlist1 = [0.08,0.15,0.1,0.11,0.07,
#     0.07,0.1,0.06,0.07,0.1,
#     0.06,0.11,0.08,0.08,0.08,
#     0.08,0.1,0.1,0.12,0.12,0.12]
#     sizelist = [10,100,10,10,10,
#     5,5,5,10,1000,
#     10,20,100,5,5,
#     5,5,5,100,10000,10000]
#     commissionlist = [1.01,2.01,3.01,0,1.51,
#     1.53,5.1,0.51,0.51,2.04,
#     0.81,1.01,1.51,0.51,0.51,
#     0.51,1.53,1.53,15.01,1.9,1.9]
#     
#     factor2 = 0.5
#     if (product =="IO"):
#     
#         factor2 = 1
#     if (product == "300" or product == "50"):
#         
#         factor2 = 0.07
#     
#     matchid = np.where(np.array(productlist) == product)[0]
#     factor1 = float(np.array(marginlist1)[matchid])
#     size = float(np.array(sizelist)[matchid])
#     commission = float(np.array(commissionlist)[matchid]) 
#     return(factor1,factor2,size,commission)
# 
# =============================================================================
