import os
import time
import json
import requests
import numpy as np
import pandas as pd
from io import StringIO
from pathlib import Path
from datetime import datetime, timedelta
from .models import StockMetaData

ROOT = Path(__file__).resolve().parent
meta_data = StockMetaData.objects.all()
stocks = [stock.__str__() for stock in meta_data]


def preprocess(x):
    return int(x.replace(',', ''))


def convert(x):
    if x == '--':
        return np.nan
    if type(x) == str:
        return float(x.replace(',', ''))
    else:
        return x


def download_stock_price(datestr):  # 下載某天股價
    r = requests.post(
        'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' +
        datestr + '&type=ALL')
    if len(r.text):
        df = pd.read_csv(StringIO(r.text.replace("=", "")),
                         header=["證券代號" in l
                                 for l in r.text.split("\n")].index(True) - 1)
        df = df[['證券代號', '開盤價', '最高價', '最低價', '收盤價', '成交股數', '本益比']]
        df.columns = ['code', 'Open', 'High', 'Low', 'Close', 'Volume', 'PE']
        stock_codes = [c.split(' ')[0] for c in stocks]
        df = df[df['code'].isin(stock_codes)].reset_index(drop=True)
        converted_df = {}
        for col in df.columns:
            converted_df[col] = df[col].apply(convert)
        return pd.DataFrame(converted_df).dropna().reset_index(drop=True)
    else:
        print(datestr, 'no data')
        return


def download_institutional_investor(date):
    # 下載某天三大法人
    r = requests.get('http://www.tse.com.tw/fund/T86?response=csv&date=' +
                     date + '&selectType=ALLBUT0999')
    try:
        df = pd.read_csv(StringIO(r.text),
                         header=1).dropna(how='all', axis=1).dropna(how='any')
    except pd.errors.EmptyDataError:
        print(f'{date} no data')
        return
    stock_codes = [c.split(' ')[0] for c in stocks]
    df = df[np.isin(df['證券代號'], stock_codes)].reset_index(drop=True)
    df['外資買進股數'] = df['外陸資買進股數(不含外資自營商)'].apply(preprocess)
    df['外資賣出股數'] = df['外陸資賣出股數(不含外資自營商)'].apply(preprocess)
    df['自營商買進股數'] = df['自營商買進股數(自行買賣)'].apply(
        preprocess) + df['自營商買進股數(避險)'].apply(preprocess)
    df['自營商賣出股數'] = df['自營商賣出股數(自行買賣)'].apply(
        preprocess) + df['自營商賣出股數(避險)'].apply(preprocess)
    df = df[[
        '證券代號', '外資買進股數', '外資賣出股數', '自營商買進股數', '自營商賣出股數', '投信買進股數', '投信賣出股數'
    ]]
    df['投信買進股數'] = df['投信買進股數'].apply(preprocess)
    df['投信賣出股數'] = df['投信賣出股數'].apply(preprocess)
    df.columns = [
        'code', 'foreign_buy', 'foreign_sell', 'dealer_buy', 'dealer_sell',
        'invest_buy', 'invest_sell'
    ]
    return df


def download_punishment(compare_date):
    # 查詢處置股票
    modify_time = os.path.getmtime(f'{ROOT}/punished.csv')
    modify_time = time.strftime('%Y%m%d', time.localtime(modify_time))
    if modify_time == compare_date:  #這天已經查過 不用再查了
        return
    end = datetime.strptime(compare_date, '%Y%m%d') + timedelta(days=1)
    end = datetime.strftime(end, '%Y%m%d')

    r = requests.post(
        f'https://www.twse.com.tw/announcement/punish?response=json&startDate={modify_time}&endDate={end}'
    )
    df = pd.DataFrame(json.loads(r.text)['data'])[[2, 6]]
    df.columns = ['code', 'duration']
    df.to_csv(f'{ROOT}/punished.csv', index=False)
