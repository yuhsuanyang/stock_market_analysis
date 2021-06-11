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
#print(root)
if datetime.now().time().hour < 14:
    ref_date = datetime.today() - timedelta(days=2)
else:
    ref_date = datetime.today()

if ref_date.isoweekday() == 6:
    adjust = 0
elif ref_date.isoweekday() == 7:
    adjust = -1
else:
    adjust = 1
today = ref_date + timedelta(days=adjust)
print('ref date: ', ref_date)
print('today: ', today)


def get_all_data():
    stocks = StockMetaData.objects.all()
    return [stocks[i].__str__() for i in range(len(stocks))]


stocks = get_all_data()


def get_latest_data():
    yesterday = today - timedelta(days=2)
    #   print('ref date', datetime.strftime(ref_date, '%Y-%m-%d'))
    #    print(today, today.isoweekday())
    #    print(yesterday, yesterday.isoweekday())
    start_date = datetime.strftime(yesterday, '%Y-%m-%d')
    end_date = datetime.strftime(today, '%Y-%m-%d')
    start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
    end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5ETWII?period1={start}&period2={end}&interval=1d&events=history&=hP2rOschxO0"
    res = requests.get(url)
    data = json.loads(res.text)
    data = data['chart']['result'][0]['indicators']['quote'][0]
    #print(data)
    return {
        'date': datetime.strftime(today - timedelta(days=1), '%Y-%m-%d'),
        'yesterday_close': round(data['close'][0], 2),
        'today_close': round(data['close'][1], 2),
        'low': round(data['low'][1], 2),
        'high': round(data['high'][1], 2),
        'open': round(data['open'][1], 2)
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
        #        print(df.code[i])

        first_row = PriceData.objects.all().filter(
            code=int(df.code[i])).order_by("Date")[0]
        print(first_row.__str__())
        #print(row.code, row.Open, row.High, row.Low, row.Close, row.Volume)
        first_row.delete()
        row.save()


def update_stock_price():
    with open(f"{root}/data_date_record.txt", "r") as f:
        last_date = f.read()
    print(last_date)
    last_date = datetime.strptime(last_date.strip(), '%Y-%m-%d')

    print('last record date: ', last_date)
    tracking_days = (today - last_date).days - 1

    if tracking_days:  # table PriceData needs to be updated
        for d in range(1, tracking_days + 1):
            datestr = datetime.strftime(last_date + timedelta(days=d),
                                        '%Y-%m-%d')
            # download data and cleaning
            one_day_data = download_stock_price(datestr.replace('-', ''))
            if type(one_day_data) == pd.DataFrame:
                #   print(one_day_data)
                update_db(one_day_data, datestr)

        with open(f"{root}/data_date_record.txt", 'w') as f:
            f.write(datestr)
    else:
        print('price data is already up to date')


def news(request):
    data = get_latest_data()
    if datetime.now().time().hour >= 14:
        update_stock_price()
    if data['today_close'] > data['yesterday_close']:
        trend = 'red'
    elif data['today_close'] < data['yesterday_close']:
        trend = 'green'
    else:
        trend = 'gold'
    data['trend'] = trend
    print(data)
    #   print(stocks[0])
    data['stock_list'] = stocks
    return render(request, 'index.html', context=data)


if __name__ == "__main__":
    get_latest_data()
    update_stock_price()
