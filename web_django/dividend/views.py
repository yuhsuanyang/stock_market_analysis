import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import DividendData
from meta_data.models import StockMetaData
from .util import create_dash
# Create your views here.

meta_data = StockMetaData.objects.all()


def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(
        reverse('dividend:dashboard', kwargs={'stock_id': stock_id}))


def create_df(model_table):
    if not len(model_table):
        return model_table
    df = {'year': [], 'season': []}
    season2word = {1.5: '上半年', 2.5: '下半年', 0: '-'}
    for col in model_table[0].get_values():
        df[col] = []
    for row in model_table:
        df['year'].append(row.year)
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


def get_raw_data(stock_id):
    table = DividendData.objects.filter(code=stock_id)
    return create_df(table)


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_raw_data(stock_id)
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
