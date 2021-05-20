import argparse
import pickle
import time

import numpy as np
import pandas as pd
import requests

import config

URLS = {'profit_loss': 'https://mops.twse.com.tw/mops/web/ajax_t163sb04',  # 綜合損益
        'asset_debt': 'https://mops.twse.com.tw/mops/web/ajax_t163sb05',  # 資產負債,
        # 每月營業收入(not necessary)
        'operation_revenue': 'https://mops.twse.com.tw/mops/web/t21sc04_ifrs',
        # 營業分析(not necessary)
        'operation_analysis': 'https://mops.twse.com.tw/mops/web/ajax_t163sb06',
        'cash_flow': 'https://mops.twse.com.tw/mops/web/ajax_t164sb05'
        }


def query_mops(year, data_type, stock_code=None, step=1):
    dfs, seasons = [], []
    form = {
        'encodeURIComponent': 1,
        'step': step,
        'firstin': 1,
        'off': 1,
        'co_id': str(stock_code),
        'TYPEK': 'sii',
        'year': str(year),
        'season': 0,
    }
    for i in range(4):
        # print(i)
        form['season'] += 1
        try:
            r = requests.post(URLS[data_type], form)
            r.encoding = 'utf8'
            dfs.append(pd.read_html(r.text, header=None))
            seasons.append(i+1)

        except Exception as e:
            print(year, i, e)
            continue
            # return dfs
    return dfs, seasons


def query_dividend(stock_code):
    url = f'https://tw.stock.yahoo.com/d/s/dividend_{stock_code}.html'
    # Encode this website by Big5
    df = pd.read_html(url, encoding="Big5")[3][[0, 1, 2, 5, 6]]
    df.columns = ['year', 'distribute_date',
                  'cash_dividend', 'stock_dividend', 'total']
    df = df.drop(0)
    df = df[df.distribute_date != '-'].reset_index(drop=True)
    year = [y.split('年')[0] for y in df.year]
    df.year = pd.DataFrame(year)
    processed_data = []

    for year in df.year.unique():
        rows = df[df.year == year]
        processed_data.append([year,
                               ' / '.join(rows.distribute_date.tolist()),
                               rows.cash_dividend.astype(float).sum(),
                               rows.stock_dividend.astype(float).sum(),
                               rows.total.astype(float).sum(), ])

    df = pd.DataFrame(processed_data, columns=df.columns)
    return df


def get_stock_meta_data():
    print('downloading data from website')
    res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    print('creating dataframe')
    df = pd.read_html(res.text)[0][[0, 2, 4]]
    df = df.drop([0, 1]).dropna().reset_index(drop=True)
    df.columns = ['full_name', 'listed_date', 'industry_type']
    code_and_name = []
    for name in df.full_name:
        rename = name.replace('\u3000', ' ').split(' ')
        code_and_name.append(rename)

    df[['code', 'name']] = pd.DataFrame(code_and_name)

    return df[['code', 'name', 'listed_date', 'industry_type']].iloc[0:952]


def merge_by_season_per_year(df_list, column_names, company_type, year):
    # company type
    #    1: bank
    #    3: standard
    #    4: holdings
    #    5: insurance
    #    6: other

    norms = {}
    for col in column_names[2:]:
        norm_data = df_list[0][company_type][['公司代號']]
        for i in range(4):
            # print(i)
            new_data = df_list[i][company_type][['公司代號', col]]
            new_data.columns = ['公司代號', '公司名稱', f"{year}_{i+1}"]
            norm_data = norm_data.merge(new_data, how='outer')
        norms[col] = norm_data
    return norms


def summary_cashflow(df_list, year, seasons):
    processed_df = []
    for df in df_list:
        cashflow_df = pd.DataFrame(pd.DataFrame(df[1]).values)[[0, 1]]
        cashflow_df = cashflow_df[cashflow_df[0].isin(
            config.cashflow_col.keys())].reset_index(drop=True).T
        cashflow_df.columns = cashflow_df.iloc[0]
        cashflow_df = cashflow_df.drop(0)
        processed_df.append(cashflow_df)

    processed_df = pd.concat(processed_df)
    processed_df.index = [f"{year}_{i}" for i in seasons]

    return processed_df


def save(filename, target):
    with open(f"../data_sample/{filename}", 'wb') as f:
        pickle.dump(target, f)


def get_cashflow_table(year, previous=None):
    stocks = pd.read_csv('../data_sample/stock_meta_data.csv')
    if previous:
        file_name = f"../data_sample/{previous}"
        cashflow_tables = pickle.load(open(file_name, 'rb'))
        start = stocks[stocks.code == max(
            cashflow_tables.keys())].index[0] + 1
    else:
        file_name = f'cashflow_tmp_{year}.pkl'
        cashflow_tables = {}
        start = 0
    anomaly = config.cashflow_anomaly
    counter = 0
    for i in range(start, len(stocks)):
        code = stocks['code'][i]
        finish = 0
        print(code)
        if code in anomaly:
            df = []
            continue
        while not finish:
            try:
                df, seasons = query_mops(year, 'cash_flow', code, 2)
                df = summary_cashflow(df, year, seasons)
                finish = 1

            except:
                print(code, "try again")
                time.sleep(10)

        cashflow_tables[code] = df
        counter += 1
        if not counter % 10:
            save(file_name, cashflow_tables)
            print('autosaved, take a break')
            time.sleep(60)

    save(file_name, cashflow_tables)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, required=True,
                        help='assign query target')
    parser.add_argument('--previous', type=str, required=False, default=None)
    parser.add_argument('--year', type=int, required=False)
    args = parser.parse_args()

    if args.target == 'meta_data':
        meta_data = get_stock_meta_data()
        meta_data.to_csv('../data_sample/stock_meta_data.csv', index=False)

    elif args.target == 'profit_loss':
        data = query(109, 'profit_loss')
        norm = merge_by_season_per_year(
            data, config.profit_loss_col['insurance'], 5, 109)

    elif args.target == 'asset_debt':
        data = query(109, 'asset_debt')
        norm = merge_by_season_per_year(
            data, config.asset_debt_col['insurance'], 5, 109)

    elif args.target == 'dividend':
        stocks = pd.read_csv('../data_sample/stock_meta_data.csv')['code']
        result = {}
        for stock_code in stocks:
            try:
                d = query_dividend(stock_code)
                result[stock_code] = d
            except:
                print(stock_code, 'fail')

        save('dividend', result)

    elif args.target == 'cash_flow':
        get_cashflow_table(args.year, args.previous)
