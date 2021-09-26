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
    DividendData.objects.all().delete()
    for stock_code in stocks:
        df = query_dividend(stock_code)
        print(stock_code)
        for i in range(len(df)):
            row = DividendData(code=int(stock_code),
                               year=df.iloc[i].year,
                               season=df.iloc[i].season,
                               distribute_date=df.iloc[i].distribute_date,
                               ex_dividend_date=df.iloc[i].ex_dividend_date,
                               cash=df.iloc[i].cash_dividend,
                               stock=df.iloc[i].stock_dividend)
            row.save()
