import requests
import pandas as pd
import numpy as np
import config

year = 109
urls = {'profit_loss':'https://mops.twse.com.tw/mops/web/ajax_t163sb04', #綜合損益
        'asset_debt': 'https://mops.twse.com.tw/mops/web/t163sb05', #資產負債,
        'operation_revenue': 'https://mops.twse.com.tw/mops/web/t21sc04_ifrs', #營業收入
        'operation_analysis': 'https://mops.twse.com.tw/mops/web/t163sb06'#, 營業分析
        #'gross': 'https://mops.twse.com.tw/mops/web/t163sb07' #毛利率(可以從綜合損益找到）
        }


def query(year, data_type):
    dfs = []
    for i in range(4):
        r = requests.post(urls[data_type], {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'sii',
        #'co_id':stock_id, 
        'year':str(year),
        'season':str(i+1),
        })
        r.encoding = 'utf8'
        dfs.append(pd.read_html(r.text, header=None))
    return dfs

def extration_by_season_per_year(df_list, column_names, year):
    company_type = 3
    norms = {}
    for col in column_names[2:]:
        norm_data = df_list[0][company_type][['公司代號', '公司名稱']]
        for i in range(4):
            print(i)
            new_data = df_list[i][company_type][['公司代號', '公司名稱', col]]
            new_data.columns = ['公司代號', '公司名稱', f"{year}_{i+1}"]
            norm_data = norm_data.merge(new_data, how='outer')
        norms[col] = norm_data
    return norms

data = query(109, 'profit_loss')
norm = extration_by_season_per_year(data, col, 109)

