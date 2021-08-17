import pandas as pd
import yfinance as yf
from django.shortcuts import render
from datetime import datetime, timedelta

# from .models import StockMetaData
from price.models import PriceData

from .util import ROOT, meta_data, download_stock_price, download_institutional_investor, download_punishment

# root = Path(__file__).resolve().parent
# print(root)  # ../meta_data
print('-' * 20)
today = datetime.today() + timedelta(days=1)
previous = today - timedelta(days=10)
print('today: ', today)
print('previous_date: ', previous)

# meta_data = StockMetaData.objects.all()
stocks = [stock.__str__() for stock in meta_data]


def get_latest_data():  # 即時爬取大資料
    start_date = datetime.strftime(previous, '%Y-%m-%d')
    end_date = datetime.strftime(today, '%Y-%m-%d')

    data = yf.download("^TWII", start=start_date, end=end_date)
    data['Date'] = data.index.astype(str)
    data = data.reset_index(drop=True)
    print(data)
    return {
        'date': data['Date'].iloc[-1],
        'yesterday_close': round(data['Close'].iloc[-2], 2),
        'today_close': round(data['Close'].iloc[-1], 2),
        'low': round(data['Low'].iloc[-1], 2),
        'high': round(data['High'].iloc[-1], 2),
        'open': round(data['Open'].iloc[1], 2)
    }


def update_price_table(df, date):
    # 更新股價db
    for i in range(len(df)):
        first_row = PriceData.objects.all().filter(
            code=int(df.code[i])).order_by("date")[0]
        row = PriceData(code=int(df.code[i]),
                        date=date,
                        key=f"{int(df.code[i])} {date}",
                        Open=df.Open[i],
                        High=df.High[i],
                        Low=df.Low[i],
                        Close=df.Close[i],
                        Volume=df.Volume[i],
                        PE=df.PE[i])

        # print(first_row.__str__())
        first_row.delete()
        row.save()


def update_stock_price(compare_date):
    # 下載股價資料+更新db
    with open(f"{ROOT}/data_date_record.txt", "r") as f:
        last_date = f.read()

    last_date = datetime.strptime(last_date.strip(), '%Y-%m-%d')
    print('last record date: ', last_date)
    tracking_days = (compare_date - last_date).days  # - 1

    if tracking_days:  # table PriceData needs to be updated
        dates = []
        for d in range(1, tracking_days + 1):
            datestr = datetime.strftime(last_date + timedelta(days=d),
                                        '%Y-%m-%d')
            # download data and cleaning
            one_day_data = download_stock_price(datestr.replace('-', ''))
            if type(one_day_data) == pd.DataFrame:
                print('updating db', datestr)
                update_price_table(one_day_data, datestr)
                dates.append(datestr)
        if len(dates):
            with open(f"{ROOT}/data_date_record.txt", 'w') as f:
                f.write(dates[-1])
            print('creating daily report')
        sum_up()  # create daily report
    else:
        print('price data is already up to date')


def sum_up():
    # 製作每日報告
    whole_data = PriceData.objects.all().order_by('-date')
    today = whole_data.values('date').distinct()[0]
    previous_day = whole_data.values('date').distinct()[1]
    # print(today, previous_day)
    data = whole_data.filter(date=today['date'])
    df = [[
        row.code,
        meta_data.filter(code=row.code)[0].name,
        meta_data.filter(code=row.code)[0].industry_type, row.Close,
        row.Volume, row.PE
    ] for row in data]
    df = pd.DataFrame(df,
                      columns=[
                          'code', 'name', 'industry_type', 'today_close',
                          'volume', 'PE'
                      ])
    previous_close = []
    for stock_code in df['code'].values:
        row = whole_data.filter(date=previous_day['date']).filter(
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
    # print(df)
    df.to_csv(f"{ROOT}/daily_report.csv", index=False)


def main(request):
    print('-' * 10, 'downloading latest data')
    data = get_latest_data()
    download_punishment(data['date'].replace('-', ''))
    if datetime.now().time().hour >= 14 or datetime.now().time(
    ).hour <= 9:  # 每天兩點以後更新股價
        print('-' * 10, 'updating stock price')
        update_stock_price(datetime.strptime(data['date'], '%Y-%m-%d'))

    # TODO: 每天五點以後更新三大法人

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
    print('-' * 20)
    print(data)
    #   print(stocks[0])
    data['stock_list'] = stocks
    return render(request, 'index.html', context=data)


# if __name__ == "__main__":
#     get_latest_data()
#     update_stock_price()
