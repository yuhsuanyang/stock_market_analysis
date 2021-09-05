import numpy as np
import pandas as pd
from pathlib import Path
from django.shortcuts import render, redirect
from django.urls import reverse

from meta_data.models import StockMetaData
from price.models import PriceData
# Create your views here.

root = str(Path(__file__).resolve().parent.parent) + '/meta_data'
#print(root)
correlation = pd.read_csv(f'{root}/daily_corr.csv')
same_trade = []
meta_data = StockMetaData.objects.all()
price_data = PriceData.objects.all().order_by('date')


def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(reverse('price:dashboard', kwargs={'stock_id': stock_id}))


def get_same_trade(industry_type):
    global same_trade
    same_trade = StockMetaData.objects.filter(industry_type=industry_type)


def get_score(stock_code):
    df = correlation[['Unnamed: 0', stock_code]]
    df.columns = ['stock_id', 'corr']
    price = PriceData.objects.filter(code=stock_code).order_by('-date')[0]
    today = price.date
    print(today)
    close = price.Close
    price = [[int(row.code), row.Close]
             for row in PriceData.objects.filter(date=today)]
    price = pd.DataFrame(price, columns=['stock_id', 'close'])
    df = df.merge(price, on='stock_id', how='left')
    df['close_sim'] = 1 - abs(np.log10(close) - np.log10(df['close']))
    same_trade_id = [row.code for row in same_trade]
    industry_sim = []
    for code in df['stock_id']:
        if str(code) in same_trade_id:
            industry_sim.append(1)
        else:
            industry_sim.append(0)
    df['industry_sim'] = pd.DataFrame(industry_sim)
    df['score'] = df['corr'] + df['close_sim'] + df['industry_sim']
    #    df['score'] = df['corr'] + df['industry_sim']
    return df


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    #    global industry_type
    #    industry_type = info.industry_type
    get_same_trade(info.industry_type)
    df = get_score(stock_id)
    print(df.sort_values(by='score', ascending=False).head(10))
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data

    data['same_trade'] = same_trade
    return render(request, 'similarity_dashboard.html', context=data)
