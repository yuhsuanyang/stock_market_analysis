import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import PriceData
from meta_data.models import StockMetaData

from .util import *

meta_data = StockMetaData.objects.all()
price_data = PriceData.objects.all().order_by('-Date')
today = str(price_data[0].Date).strip()
stock_code = ''
history = pd.DataFrame([])


# Create your views here.
def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(reverse('price:welcome', kwargs={'stock_id': stock_id}))


# reverse 的用法與意義：https://blog.csdn.net/qq_33867131/article/details/81910860


def color(price1, price2):
    if price1 > price2:
        return 'red'
    elif price1 < price2:
        return 'green'
    else:
        return 'black'


def get_price(stock_id):
    global stock_code
    global history
    stock_code = stock_id
    #print(stock_code)
    history = query_historical_price(stock_code, today)
    #print(history)
    today_stock_price = price_data.filter(code=stock_id)[0]
    print(today_stock_price.Date)
    yesterday_close = price_data.filter(
        code=stock_id).order_by('-Date')[1].Close
    updown = round(today_stock_price.Close - yesterday_close, 2)
    data = {
        'today_date': today_stock_price.Date,
        'open_color': color(today_stock_price.Open, yesterday_close),
        'open': today_stock_price.Open,
        'high_color': color(today_stock_price.High, yesterday_close),
        'high': today_stock_price.High,
        'low_color': color(today_stock_price.Low, yesterday_close),
        'low': today_stock_price.Low,
        'close_color': color(today_stock_price.Close, yesterday_close),
        'close': today_stock_price.Close,
        'updown': updown,
        'volume': today_stock_price.Volume / 1000,
        'previous_close': yesterday_close,
        'amplitude': round(updown * 100 / yesterday_close, 2)
    }
    return data


def welcome(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    data = get_price(stock_id)
    app = create_dash(stock_code, info.name, history)

    data['stock_id'] = f"{stock_id} {info.name}"
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    return render(request, 'price_dashboard.html', context=data)


#def try_dash(request):
#    context = {}
#    return render(request, 'welcome.html', context)


def price_visualizer():
    whole_data = query_historical_price(stock_code, today)
    return whole_data


#historical_stock_price = price_visualizer()
#print(historical_stock_price)
