import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import PriceData, InstitutionalInvestorData
from meta_data.models import StockMetaData

from .util import *

root = Path(__file__).resolve().parent.parent  # ../web_django

meta_data = StockMetaData.objects.all()
institutional_data = InstitutionalInvestorData.objects.all()
stock_code = ''
history = pd.DataFrame([])
punished = pd.read_csv(f'{root}/meta_data/punished.csv')


# Create your views here.
def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(reverse('price:dashboard', kwargs={'stock_id': stock_id}))


# reverse 的用法與意義：https://blog.csdn.net/qq_33867131/article/details/81910860


def color(price1, price2):  #price2: 昨收
    #return: background_color, font_color
    if price1 > price2:
        if (price1 - price2) / price2 >= 0.095:
            return 'red', 'white'
        else:
            return 'white', 'red'
    elif price1 < price2:
        if (price1 - price2) / price2 <= -0.095:
            return 'green', 'white'
        else:
            return 'white', 'green'
    else:
        return 'white', 'black'


def get_price(stock_id, today, price_data):
    global stock_code
    global history
    stock_code = stock_id
    end_date = datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    #print(stock_code)
    history = query_historical_price(stock_code, end_date)
    #print(history.iloc[-10:])
    today_stock_price = price_data.filter(code=stock_id)[0]
    print(today_stock_price.date)
    yesterday_close = price_data.filter(
        code=stock_id).order_by('-date')[1].Close
    updown = round(today_stock_price.Close - yesterday_close, 2)
    today_price_values = today_stock_price.get_values()
    data = {
        'today_date': today_stock_price.date,
        'updown': updown,
        'volume': today_stock_price.Volume / 1000,
        'previous_close': yesterday_close,
        'amplitude': round(updown * 100 / yesterday_close, 2),
        'PE': today_stock_price.PE,
        'punishment_duration': False
    }
    #    print(punished['code'])
    if int(stock_code) in punished['code'].values:
        duration = punished[punished.code == int(
            stock_code)]['duration'].values[0].split('～')
        data['punishment_duration'] = duration[0][4:] + '~' + duration[1][4:]
    for col in today_price_values:
        data[col] = today_price_values[col]
        colors = color(today_price_values[col], yesterday_close)
        data[f'{col}_highlight_color'] = colors[0]
        data[f'{col}_color'] = colors[1]

    data['updown_color'] = [
        c for c in [data['close_color'], data['close_highlight_color']]
        if c != 'white'
    ][0]
    print(data)
    return data


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    price_data = PriceData.objects.all().order_by('-date')
    today = str(price_data[0].date).strip()
    same_trade_price_data = price_data.filter(
        code__in=[stock.code for stock in same_trade]).filter(date=today)
    same_trade_PE_mean = np.mean([stock.PE for stock in same_trade_price_data])
    data = get_price(stock_id, today, price_data)
    app = create_dash(stock_code, info.name, history)

    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    data['PE_mean'] = round(same_trade_PE_mean, 2)
    #    data['profit_loss_url'] = info.get_profit_loss_url
    return render(request, 'price_dashboard.html', context=data)


def try_dash(request):
    context = {}
    return render(request, 'welcome.html', context)


#def price_visualizer():
#    whole_data = query_historical_price(stock_code, today)
#    return whole_data

#historical_stock_price = price_visualizer()
#print(historical_stock_price)
