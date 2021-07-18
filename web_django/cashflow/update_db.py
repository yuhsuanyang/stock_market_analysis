import time
import requests
import argparse
import pandas as pd
from meta_data.models import StockMetaData
from .models import CashflowData

url = 'https://mops.twse.com.tw/mops/web/ajax_t164sb05'

terms = {
    '營運產生之現金流入（流出）': 'cash_from_operation',
    '營業活動之淨現金流入（流出）': 'cash_from_operation_activities',
    '取得不動產、廠房及設備': 'real_estate',
    '取得不動產及設備': 'real_estate',
    '投資活動之淨現金流入（流出）': 'cash_from_investment',
    '籌資活動之淨現金流入（流出）': 'cash_from_fundraise'
}

stocks = [stock for stock in StockMetaData.objects.all()]


def crawl(year, season, stock_code, step=1):
    form = {
        'encodeURIComponent': 1,
        'step': step,
        'firstin': 1,
        'off': 1,
        'co_id': str(stock_code),
        'TYPEK': 'sii',
        'year': str(year),
        'season': season,
    }
    r = requests.post(url, form)
    r.encoding = 'utf8'
    df = pd.read_html(r.text, header=None)[-1]
    df.columns = [i for i in range(len(df.columns))]
    df = df[[0, 1]]
    data = {terms[term]: 0 for term in terms}
    for term in terms:
        if len(df[df[0] == term]):
            data[terms[term]] = df[df[0] == term][1].values[0]


#        else:
#            data[terms[term]] = 0

    return data


def create_row(code, data, season):
    cashflow_data_row = CashflowData(
        code=code,
        season=season,
        cash_from_operation=data['cash_from_operation'],
        cash_from_operation_activities=data['cash_from_operation_activities'],
        real_estate=data['real_estate'],
        cash_from_investment=data['cash_from_investment'],
        cash_from_fundraise=data['cash_from_fundraise'])
    cashflow_data_row.save()


def main(action, year, season):
    if action == 'add_data':
        for i, stock in enumerate(stocks):
            id_ = stock.code
            print(id_)
            if stock.company_type in ['bank', 'holdings', 'insurance']:
                data = crawl(year, season, id_, 2)
            else:
                data = crawl(year, season, id_)
            create_row(id_, data, f"{year}_{season}")
            if not i % 10 and i > 0:
                print('take a 1-min break....')
                time.sleep(60)

    elif action == 'delete_data':
        CashflowData.objects.filter(season=f"{year}_{season}").delete()


if __name__ == "__name__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, default='add_data')
    parser.add_argument('--year', type=str, required=True)
    parser.add_argument('--season', type=str, required=True)
    args = parser.parse_args()
    main(args.action, args.year, args.season)
