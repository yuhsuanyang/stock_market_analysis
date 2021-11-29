import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .models import DividendData
from meta_data.models import StockMetaData

meta_data = StockMetaData.objects.all()
stocks = [stock.code for stock in meta_data]


def convert_date_form(x):
    return x.replace('/', '-')


def query_dividend(stock_code):
    url = f"https://tw.stock.yahoo.com/d/s/dividend_{stock_code}.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    result = soup.find_all("li", class_="List(n)")
    data = []
    for r in result:
        cells = r.find_all("div")
        try:
            if len(cells[0].text) >= 4 and int(cells[0].text[0:4]) > 2010:
                if 'Q' in cells[2].text:
                    one_data = cells[2].text.split('Q')
                elif 'H' in cells[2].text:
                    one_data = cells[2].text.split('H')
                    one_data[1] = one_data[1] + '.5'
                else:
                    one_data = [cells[2].text, '0']

                one_data[0] = int(one_data[0]) - 1911
                for i in [3, 4, 6, 7]:
                    one_data.append(cells[i].text)

                data.append(one_data)
        except:
            break
    df = pd.DataFrame(data,
                      columns=[
                          'year', 'season', 'cash_dividend', 'stock_dividend',
                          'ex_dividend_date', 'distribute_date'
                      ])

    drop_index = df[(df.distribute_date == '-') |
                    (df.ex_dividend_date == '尚未公布')].index
    df = df.drop(drop_index)
    df['ex_dividend_date'] = df['ex_dividend_date'].apply(convert_date_form)
    df['distribute_date'] = df['distribute_date'].apply(convert_date_form)
    return df


def main():
    counter = 0
    no_dividend = []
    for i, stock_code in enumerate(stocks):
        df = query_dividend(stock_code)
        if not len(df):
            no_dividend.append(stock_code)
            continue
        else:
            counter += 1

        historical_data = DividendData.objects.filter(code=stock_code)
        if len(historical_data):
            latest_data = historical_data.order_by('-year', '-season')[0]
            latest_year = latest_data.year
            latest_season = latest_data.season
        else:
            latest_year = 101
            latest_season = 0
        if (latest_year != df.iloc[0].year) and (latest_season !=
                                                 df.iloc[0].season):
            row = DividendData(code=int(stock_code),
                               year=df.iloc[0].year,
                               season=df.iloc[0].season,
                               distribute_date=df.iloc[0].distribute_date,
                               ex_dividend_date=df.iloc[0].ex_dividend_date,
                               cash=df.iloc[0].cash_dividend,
                               stock=df.iloc[0].stock_dividend)
            row.save()
            print(stock_code, 'update dividend')
        if not i % 10 and i > 0:
            print('take a 1-min break ...')
            time.sleep(30)
    print(counter, 'companies have founded dividend')
    return no_dividend
