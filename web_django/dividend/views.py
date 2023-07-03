import pandas as pd
from django.shortcuts import render
from meta_data.models import StockMetaData
from profit_loss.models import *
from .models import DividendData
from .util import create_dash
# Create your views here.

meta_data = StockMetaData.objects.all()
profit_loss_table_dict = {
    'holdings': HoldingsProfitLossData,
    'bank': BankProfitLossData,
    'insurance': InsuranceProfitLossData,
    'standard': StandardProfitLossData
}


def create_df(dividend_table, profit_loss_table):
    if not len(dividend_table):
        return dividend_table
    df = {'year': [], 'season': [], 'year_EPS': []}
    season2word = {1.5: '上半年', 2.5: '下半年', 0: '-'}
    for col in dividend_table[0].get_values():
        df[col] = []
    for row in dividend_table:
        df['year'].append(row.year)
        if row.year >= 105 and row.season in [0, 2.5, 4]:
            #        print(f"{row.year}_4")
            eps = profit_loss_table.filter(season=f"{row.year}_4")
            if len(eps):
                eps = eps[0].EPS
            else:
                eps = '-'
        else:
            eps = '-'
        df['year_EPS'].append(eps)
        if row.season in season2word:
            df['season'].append(season2word[row.season])
        else:
            df['season'].append(row.season)
        row_values = row.get_values()
        for col in row_values:
            df[col].append(row_values[col])
    df = pd.DataFrame.from_dict(df).sort_values(
        by=['year', 'season']).reset_index(drop=True)
    return df


def get_raw_data(stock_id, company_type):
    profit_loss_table = profit_loss_table_dict[company_type].objects.filter(
        code=stock_id)
    dividend_table = DividendData.objects.filter(code=stock_id)
    return create_df(dividend_table, profit_loss_table)


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_raw_data(stock_id, info.company_type)
    print(df)
    app = create_dash(df)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    data['stock_info'] = info
    return render(request, 'dividend_dashboard.html', context=data)
