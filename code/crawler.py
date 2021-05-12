import requests
import pandas as pd
import numpy as np
import config


urls = {'profit_loss':'https://mops.twse.com.tw/mops/web/ajax_t163sb04', #綜合損益
        'asset_debt': 'https://mops.twse.com.tw/mops/web/ajax_t163sb05', #資產負債,
        'operation_revenue': 'https://mops.twse.com.tw/mops/web/t21sc04_ifrs', #每月營業收入
        'operation_analysis': 'https://mops.twse.com.tw/mops/web/ajax_t163sb06', # 營業分析
        'dividend': 'https://mops.twse.com.tw/mops/web/ajax_t05st09' #股利政策
        }


def query(year, data_type):
    dfs = []
    for i in range(4):
        print(i)
        try:
            r = requests.post(urls[data_type], {
                    'encodeURIComponent':1,
                    'step':1,
                    'firstin':1,
                    'off':1,
                    'TYPEK':'sii',
                    'year':str(year),
                    'season':str(i+1),
                    })
            r.encoding = 'utf8'
            dfs.append(pd.read_html(r.text, header=None))
        except Exception as e:
            print(e)
            return dfs
    return dfs

def summary_by_season_per_year(df_list, column_names, company_type, year):
    # company type
#    1: bank
#    3: standard
#    4: holdings
#    5: insurance
#    6: other

    norms = {}
    for col in column_names[2:]:
        norm_data = df_list[0][company_type][['公司代號', '公司名稱']]
        for i in range(4):
            #print(i)
            new_data = df_list[i][company_type][['公司代號', '公司名稱', col]]
            new_data.columns = ['公司代號', '公司名稱', f"{year}_{i+1}"]
            norm_data = norm_data.merge(new_data, how='outer')
        norms[col] = norm_data
    return norms

#---get stock meta data---------
res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
df = pd.read_html(res.text)[0]
#-------query profit_loss-------------
data = query(109, 'profit_loss')
norm =  summary_by_season_per_year(data, config.profit_loss_col['insurance'], 5, 109)

#------query asset_debt-----------
data = query(109, 'asset_debt')
norm =  summary_by_season_per_year(data, config.asset_debt_col['insurance'], 5, 109)

#----query operation revenue------
data = query(109, 'operation_analysis')

# TODO: query financial table  https://medium.com/renee0918/python%E7%88%AC%E8%9F%B2-%E5%80%8B%E8%82%A1%E6%AF%8F%E5%AD%A3%E8%B2%A1%E5%A0%B1-a83d1e21d9ca