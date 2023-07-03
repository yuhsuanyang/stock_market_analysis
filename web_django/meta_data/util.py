import os
import time
import json
import requests
import numpy as np
import pandas as pd
from io import StringIO
from pathlib import Path
from bs4 import BeautifulSoup
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

def download_meta_data():
    url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    res = requests.get(url)
    df = pd.read_html(res.text)[0]
    df.columns = df.iloc[0]
    df = df.drop([0,1])
    df['code'] = df['有價證券代號及名稱'].apply(lambda x: x.split('\u3000')[0])
    return df

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
    r = requests.get('http://www.twse.com.tw/fund/T86?response=csv&date=' +
                     date + '&selectType=ALL')
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


def download_profile(stock_code):
    url = f'https://tw.stock.yahoo.com/quote/{stock_code}.TW/profile'
    res = requests.get(url)
    res.encoding = 'utf-8'
    table = soup.find('div', class_='table-grid row-fit-half')
    keys = [span.text for span in table.find_all('span', class_='')]
    values = [div.text for div in table.find_all('div', class_='Py(8px) Pstart(12px) Bxz(bb)')]
    data = {key: value for key, value in zip(keys, values)}
    return data

def download_new_listing(date):
    url = f'https://www.twse.com.tw/rwd/zh/company/newlisting?date={date}&response=json'
    res = requests.get(url)
    res.encoding = 'utf-8'
    data = json.loads(res.text)
    df = pd.DataFrame(data['data'], columns=data['fields'])[['公司代號', '公司簡稱', '股票上市買賣日期']]
    listed_date = []
    for date in df['股票上市買賣日期']:
        year, month, day = date.split('.')
        year = str(int(year) + 1911)
        listed_date.append('/'.join([year, month, date]))
    df['listed_date'] = pd.DataFrame(listed_date)
    meta_data = download_meta_data()[['code', '產業別']]
    meta_data = meta_data[meta_data['code'].isin(df['公司代號'])]
    df = df.merge(meta_data, left_on='公司代號', right_on='code')
    return df


def download_delisting(date):
    url = f'https://www.twse.com.tw/rwd/zh/company/suspendListing?date={date}&response=json'
    res = requests.get(url)
    res.encoding = 'utf-8'
    data = json.loads(res.text)
    df = pd.DataFrame(data['data'], columns=data['fields'])[['上市編號', '公司名稱', '終止上市日期']]
    return df

        
