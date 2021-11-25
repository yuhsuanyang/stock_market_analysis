import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from django.shortcuts import render
from meta_data.models import StockMetaData
from price.models import PriceData, InstitutionalInvestorData
from .util import create_dash
from dashboard_utils.common_functions import create_price_sequence

meta_data = StockMetaData.objects.all()
price_data = PriceData.objects.all()
institutional_data = InstitutionalInvestorData.objects.all()


# Create your views here.
def download(stock_code):
    url1 = f"https://concords.moneydj.com/z/zc/zcj/zcj_{stock_code}.djhtm"
    url2 = f"https://concords.moneydj.com/z/zc/zcm/zcm_{stock_code}.djhtm"
    res = requests.get(url1)
    soup = BeautifulSoup(res.text, "lxml")
    table = soup.select('table')[-1]
    date = table.find_all("div", "t11")[0].text
    data = table.find_all("td", class_=['t3n1', 't3t1', 't3r1'])
    data = np.array([cell.text for cell in data]).reshape(-1, 4)
    data = pd.DataFrame(data, columns=['term', 'amount', 'increment', 'ratio'])
    data['amount'] = data['amount'].apply(lambda x: x.replace(',', ''))
    data['increment'] = data['increment'].apply(lambda x: x.replace(',', ''))
    data['ratio'] = data['ratio'].apply(lambda x: x.replace('%', ''))
    data = data.replace('', '0.0')

    res = requests.get(url2)
    soup = BeautifulSoup(res.text, "lxml")
    total_amount = soup.select('table')[-1].find_all(
        'td', class_='t3n1')[0].text.replace(',', '')
    data = data.append(
        {
            'term': '其他',
            'amount': int(total_amount) - data['amount'].astype(int).sum(),
            'ratio': 100 - data['ratio'].astype(float).sum()
        },
        ignore_index=True)
    return date, data, total_amount


def get_institutional(stock_code):
    institutional = institutional_data.filter(
        code=stock_code).order_by('-date')
    df = []
    columns = list(institutional[0].get_values().keys())
    for row in institutional:
        values = row.get_values()
        df.append([row.date] + [values[k] for k in values])
    df = pd.DataFrame(df, columns=['date'] + columns)
    df['foreign'] = df['foreign_buy'] - df['foreign_sell']
    df['invest'] = df['invest_buy'] - df['invest_sell']
    df['dealer'] = df['dealer_buy'] - df['dealer_sell']
    return df[['date', 'foreign', 'invest', 'dealer']]


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    date, chip_df, total = download(stock_id)
    institution_df = get_institutional(stock_id)
    price = price_data.filter(code=stock_id).order_by('-date')
    price_df = create_price_sequence(price)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    data['stock_info'] = info
    app = create_dash(chip_df, institution_df, price_df)
    print(date)
    print(chip_df)
    print(total)
    return render(request, 'chip_dashboard.html', context=data)
