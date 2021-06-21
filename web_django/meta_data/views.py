import os
import json
import time
import requests
import numpy as np
import pandas as pd
from io import StringIO
from pathlib import Path
from django.shortcuts import render
from datetime import datetime, timedelta

from .models import StockMetaData
from price.models import PriceData

root = Path(__file__).resolve().parent
#print(root)  # ../meta_data

today = datetime.today() + timedelta(days=1)
previous = today - timedelta(days=10)
print('today: ', today)
print('previous_date: ', previous)

with open(f"{root}/data_date_record.txt", "r") as f:
    last_date = f.read()
print(last_date)
last_date = datetime.strptime(last_date.strip(), '%Y-%m-%d')

print('last record date: ', last_date)
meta_data = StockMetaData.objects.all()
stocks = [stock.__str__() for stock in meta_data]
#def get_all_data():
#    stocks = StockMetaData.objects.all()
#    return [stocks[i].__str__() for i in range(len(stocks))]
#
#stocks = get_all_data()


def get_latest_data():
    start_date = datetime.strftime(previous, '%Y-%m-%d')
    end_date = datetime.strftime(today, '%Y-%m-%d')
    start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
    end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5ETWII?period1={start}&period2={end}&interval=1d&events=history&=hP2rOschxO0"
    res = requests.get(url)
    data = json.loads(res.text)
    timestamps = data['chart']['result'][0]['timestamp']
    now_date = time.strftime('%Y-%m-%d', time.localtime(timestamps[-1]))
    data = pd.DataFrame(data['chart']['result'][0]['indicators']['quote'][0])
    data['Date'] = pd.DataFrame(timestamps)
    print(data)
    data = data.dropna()
    #    print(timestamps)
    return {
        'date': now_date,
        'yesterday_close': round(data['close'].iloc[-2], 2),
        'today_close': round(data['close'].iloc[-1], 2),
        'low': round(data['low'].iloc[-1], 2),
        'high': round(data['high'].iloc[-1], 2),
        'open': round(data['open'].iloc[1], 2)
    }


def convert(x):
    if x == '--':
        return np.nan
    if type(x) == str:
        return float(x.replace(',', ''))
    else:
        return x


def download_stock_price(datestr):
    r = requests.post(
        'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' +
        datestr + '&type=ALL')
    if len(r.text):
        df = pd.read_csv(StringIO(r.text.replace("=", "")),
                         header=["證券代號" in l
                                 for l in r.text.split("\n")].index(True) - 1)
        df = df[['證券代號', '開盤價', '最高價', '最低價', '收盤價', '成交股數']]
        df.columns = ['code', 'Open', 'High', 'Low', 'Close', 'Volume']
        stock_codes = [c.split(' ')[0] for c in stocks]
        df = df[df['code'].isin(stock_codes)].reset_index(drop=True)
        converted_df = {}
        for col in df.columns:
            converted_df[col] = df[col].apply(convert)
        return pd.DataFrame(converted_df).dropna().reset_index(drop=True)
    else:
        print(datestr, 'no data')
        return


def update_db(df, date):
    for i in range(len(df)):
        row = PriceData(code=int(df.code[i]),
                        Date=date,
                        Open=df.Open[i],
                        High=df.High[i],
                        Low=df.Low[i],
                        Close=df.Close[i],
                        Volume=df.Volume[i])

        first_row = PriceData.objects.all().filter(
            code=int(df.code[i])).order_by("Date")[0]
        #print(first_row.__str__())
        first_row.delete()
        row.save()


def update_stock_price():
    tracking_days = (today - last_date).days - 1

    if tracking_days:  # table PriceData needs to be updated
        dates = []
        for d in range(1, tracking_days + 1):
            datestr = datetime.strftime(last_date + timedelta(days=d),
                                        '%Y-%m-%d')
            # download data and cleaning
            one_day_data = download_stock_price(datestr.replace('-', ''))
            if type(one_day_data) == pd.DataFrame:
                #   print(one_day_data)
                update_db(one_day_data, datestr)
                dates.append(datestr)
        if len(dates):
            with open(f"{root}/data_date_record.txt", 'w') as f:
                f.write(dates[-1])
            sum_up()  # create daily report
    else:
        print('price data is already up to date')


def query_punishment(compare_date):
    modify_time = os.path.getmtime(f'{root}/punished.csv')
    modify_time = time.strftime('%Y%m%d', time.localtime(modify_time))
    if modify_time == compare_date:  #這天已經查過 不用再查了
        return
    end = datetime.strftime(compare_date, '%Y%m%d') + timedelta(days=1)
    end = datetime.strptime(end, '%Y%m%d')

    r = requests.post(
        f'https://www.twse.com.tw/announcement/punish?response=json&startDate={start}&endDate={end}'
    )
    df = pd.DataFrame(json.loads(r.text)['data'])[[2, 6]]
    df.columns = ['code', 'duration']
    df.to_csv(f'{root}/punished.csv', index=False)


def sum_up():
    whole_data = PriceData.objects.all().order_by('-Date')
    today = whole_data.values('Date').distinct()[0]
    previous_day = whole_data.values('Date').distinct()[1]
    #print(today, previous_day)
    data = whole_data.filter(Date=today['Date'])
    df = [[
        row.code,
        meta_data.filter(code=row.code)[0].name, row.Close, row.Volume
    ] for row in data]
    df = pd.DataFrame(df, columns=['code', 'name', 'today_close', 'volume'])
    previous_close = []
    for stock_code in df['code'].values:
        row = whole_data.filter(Date=previous_day['Date']).filter(
            code=stock_code)
        if len(row):
            previous_close.append([stock_code, row[0].Close])
    df = df.merge(pd.DataFrame(previous_close,
                               columns=['code', 'previous_close']),
                  how='left')
    df['volume'] = df['volume'] / 1000
    df['updowns'] = round(df['today_close'] - df['previous_close'], 2)
    df['fluctuation'] = round((df['today_close'] - df['previous_close']) *
                              100 / df['previous_close'], 2)
    df['code'] = df['code'] + ' ' + df['name']
    del df['name']
    print(df)
    df.to_csv(f"{root}/daily_report.csv", index=False)


def news(request):
    data = get_latest_data()
    query_punishment(data['date'].replace('-', ''))
    if datetime.now().time().hour >= 14 or datetime.now().time().hour <= 9:
        update_stock_price()

    if data['today_close'] > data['yesterday_close']:
        trend_light = 'pink'
        trend = 'red'
    elif data['today_close'] < data['yesterday_close']:
        trend_light = 'lightgreen'
        trend = 'green'
    else:
        trend_light = 'lightgrey'
        trend = 'gold'
    data['trend'] = trend
    data['trend_background'] = trend_light
    print(data)
    #   print(stocks[0])
    data['stock_list'] = stocks
    return render(request, 'index.html', context=data)


if __name__ == "__main__":
    get_latest_data()
    update_stock_price()
