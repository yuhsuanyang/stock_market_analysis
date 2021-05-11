import requests
import pandas as pd
import numpy as np

year = 109
season = 4
urls = {'profit_loss':'https://mops.twse.com.tw/mops/web/ajax_t163sb04', #綜合損益
        'asset_debt': 'https://mops.twse.com.tw/mops/web/t163sb05', #資產負債,
        'operation_revenue': 'https://mops.twse.com.tw/mops/web/t21sc04_ifrs', #營業收入
        'operation_analysis': 'https://mops.twse.com.tw/mops/web/t163sb06'#, 營業分析
        #'gross': 'https://mops.twse.com.tw/mops/web/t163sb07' #毛利率(可以從綜合損益找到）
        }

data_type = 'gross'

def query(year, season, data_type):
    r = requests.post(urls[data_type], {
        'encodeURIComponent':1,
        'step':1,
        'firstin':1,
        'off':1,
        'TYPEK':'sii',
        #'co_id':stock_id, 
        'year':str(year),
        'season':str(season),
        })
    r.encoding = 'utf8'
    dfs = pd.read_html(r.text, header=None)
    return dfs

