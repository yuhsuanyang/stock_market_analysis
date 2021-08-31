import pandas as pd
from .models import DividendData
from meta_data.models import StockMetaData

meta_data = StockMetaData.objects.all()
stocks = [stock.code for stock in meta_data]


def query_dividend(stock_code):
    url = f"https://tw.stock.yahoo.com/d/s/dividend_{stock_code}.html"
    season_dict = {
        '第一季': 1,
        '第二季': 2,
        '第三季': 3,
        '第四季': 4,
        '上半': 1.5,
        '下半': 2.5
    }
    df = pd.read_html(url, encoding="cp950")[3][[0, 1, 2, 5, 6]]
    df.columns = [
        'year', 'distribute_date', 'cash_dividend', 'stock_dividend', 'total'
    ]
    df = df.drop(0)
    df = df[df.distribute_date != '-'].reset_index(drop=True)

    processed_data = []

    for i in range(len(df)):
        year = df.iloc[i].year.split('年')
        #print(year)
        if len(year[1]) > 1:
            season = season_dict[year[1]]
        else:
            season = 0

        processed_data.append([
            int(year[0]),
            season,
            df.iloc[i].distribute_date,
            df.iloc[i].cash_dividend,
            df.iloc[i].stock_dividend,
            df.iloc[i].total,
        ])

    df = pd.DataFrame(processed_data,
                      columns=[
                          'year', 'season', 'distribute_date', 'cash_dividend',
                          'stock_dividend', 'total'
                      ])
    return df


def main():
    DividendData.objects.all().delete()
    for stock_code in stocks:
        df = query_dividend(stock_code)
        for i in range(len(df)):
            row = DividendData(code=int(stock_code),
                               year=df.iloc[i].year,
                               season=df.iloc[i].season,
                               date=df.iloc[i].distribute_date,
                               cash=df.iloc[i].cash_dividend,
                               stock=df.iloc[i].stock_dividend)
            row.save()
        print(stock_code)
