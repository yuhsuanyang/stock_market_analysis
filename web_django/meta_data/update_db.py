import pandas as pd
from datetime import datetime
from django.apps import apps
from .models import StockMetaData
from price.models import PriceData, InstitutionalInvestorData

from .util import download_stock_price, download_institutional_investor, download_delisting
from dashboard_utils.model_checker import Checker

models = [model for model in apps.get_models() if hasattr(model, 'get_columns')]

def update_price_table(df, date):
    # 更新股價db
    for i in range(len(df)):
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
        row.save()


def update_institutional_table(df, date):
    for i in range(len(df)):
        row = InstitutionalInvestorData(code=int(df.code[i]),
                                        date=date,
                                        key=f'{int(df.code[i])} {date}',
                                        foreign_buy=df.foreign_buy[i],
                                        foreign_sell=df.foreign_sell[i],
                                        invest_buy=df.invest_buy[i],
                                        invest_sell=df.invest_sell[i],
                                        dealer_buy=df.dealer_buy[i],
                                        dealer_sell=df.dealer_sell[i])
        row.save()


def delete_delisting():
    data = download_delisting(datetime.today().strftime('%Y-%m-%d'))
    for code in data['上市編號']:
        for model in models:
            model.objects.filter(code=code).delete()


def add_listing(df):
    for i in range(len(df)):
        row = StockMetaData(
                code=df['code'].iloc[i],
                name=df['公司簡稱'].iloc[i],
                listed_date=df['listed_date'].iloc[i],
                industry_type=df['產業別'].iloc[i],
                company_type=standard
                )
        row.save()
    checker = Checker(PriceData)
    dates = [date.strftime('%Y%-%m-%d') for date in checker.get_unique_values('date')]




def main(date, mode):
    # date: yyyy-mm-dd
    if mode == 'price':
        print(f'downloading {date} data...')
        data = download_stock_price(date.replace('-', ''))
        if type(data) == pd.DataFrame:
            update_price_table(data, date)

    if mode == 'institutional':
        data = download_institutional_investor(date.replace('-', ''))
        if type(data) == pd.DataFrame:
            update_institutional_table(data, date)
