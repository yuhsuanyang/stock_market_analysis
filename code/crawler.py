# -*- coding: utf-8 -*
import argparse
import pickle
import time
from io import StringIO

import pandas as pd
import requests

import config

URLS = {'profit_loss': 'https://mops.twse.com.tw/mops/web/ajax_t163sb04',  # 綜合損益
        'asset_debt': 'https://mops.twse.com.tw/mops/web/ajax_t163sb05',  # 資產負債,
        # 每月營業收入(not necessary)
        'operation_revenue': 'https://mops.twse.com.tw/mops/web/t21sc04_ifrs',
        # 營業分析(not necessary)
        'operation_analysis': 'https://mops.twse.com.tw/mops/web/ajax_t163sb06',
        'cash_flow': 'https://mops.twse.com.tw/mops/web/ajax_t164sb05'  # 現金流量表
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
    url = f"https://tw.stock.yahoo.com/d/s/dividend_{stock_code}.html"
    season_dict = {'第一季': 1, '第二季': 2, '第三季': 3, '第四季': 4,
                  '上半': 1.5, '下半': 2.5}
    # Encode this website by Big5
    df = pd.read_html(url, encoding="cp950")[3][[0, 1, 2, 5, 6]]
    df.columns = ['year', 'distribute_date',
                  'cash_dividend', 'stock_dividend', 'total']
    df = df.drop(0)
    df = df[df.distribute_date != '-'].reset_index(drop=True)
    # year = [y.split('年')[0] for y in df.year]
    # df.year = pd.DataFrame(year)
    processed_data = []
    
    for i in range(len(df)):
        year = df.iloc[i].year.split('年')
        #print(year)
        if len(year[1]) > 1:
            season = season_dict[year[1]]
        else:
            season = 0
            
        processed_data.append([int(year[0]),
                               season,
                               df.iloc[i].distribute_date,
                               df.iloc[i].cash_dividend,
                               df.iloc[i].stock_dividend,
                               df.iloc[i].total,
                               ])

   

    df = pd.DataFrame(processed_data, columns=['year', 'season', 'distribute_date',
                  'cash_dividend', 'stock_dividend', 'total'])
    return df


def query_price_history(stock_code):
    start = int(time.mktime(time.strptime('2016-01-01', '%Y-%m-%d')))
    end = int(time.time())  # now
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_code}.TW?period1={start}&period2={end}&interval=1d&events=history&crumb=DCkS0u002FOZyL"
    res = requests.get(url)
    return pd.read_csv(StringIO(res.text))


def summary_cashflow(df_list, year, seasons):
    processed_df = []
    for df in df_list:
        cashflow_df = pd.DataFrame(pd.DataFrame(df[-1]).values)[[0, 1]]
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
    counter = time.time()
    for i in range(start, len(stocks)):
        code = stocks['code'][i]
        listed_year = int(stocks['listed_date'][i].split('/')[0]) - 1911
        finish = 0
        print(code)
        # if code in anomaly:
        if (listed_year-1) >= year:
            print(f'    {listed_year} listed')
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
        # counter += 1
        if (time.time()-counter) > 10:
            save(file_name, cashflow_tables)
            print('autosaved, take a break')
            time.sleep(60)
            counter = time.time()

    save(file_name, cashflow_tables)


def get_historical_price():
    stocks = pd.read_csv('../data_sample/stock_meta_data.csv')
    price_dict = {}

    for stock_id in stocks.code:
        df = query_price_history(stock_id)
        price_dict[stock_id] = df
        print(stock_id)
    save('stock_price.pkl', price_dict)


def get_multiple_company_tables(term, company_columns, company_column_names, company_type):
    raw_data = {}
    for year in range(105, 110):
        print(year)
        data, _ = query_mops(year, term)
        for i in company_type:
            print(i)
            for season in range(4):
                selected_columns = []
                columns = [('year', 'code')] + [(f"{year}_{season+1}", col_names) 
                                               for col_names in company_column_names[i]]
                for col in company_columns[company_type[i]]:
                    if col in data[season][i].columns:
                        selected_columns.append(col)
                        # print(col)
                        # if col != '公司代號':
                        #    columns.append((f"{year}_{season+1}", col))
        #        print(columns)
                data1 = data[season][i][selected_columns]
        #        print(data1.columns)
                data1.columns = pd.MultiIndex.from_tuples(columns)
                if year == 105 and season == 0:
                    raw_data[i] = data1
                else:
                    raw_data[i] = raw_data[i].merge(
                        data1, on=[('year', 'code')], how='outer')

    for i in raw_data:
        raw_data[i].to_csv(
            f'../data_sample/{term}/{company_type[i]}_{term}.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=str, required=True,
                        help='assign query target')
    parser.add_argument('--previous', type=str,
                        required=False, default=None)
    parser.add_argument('--year', type=int, required=False)
    args = parser.parse_args()

    if args.target == 'meta_data':
        meta_data = get_stock_meta_data()
        meta_data.to_csv('../data_sample/stock_meta_data.csv', index=False)

    elif args.target == 'profit_loss':
        company_type = {1: 'bank', 3: 'standard',
                        4: 'holdings', 5: 'insurance', 6: 'other'}

        company_columns_names = {1: ['利息淨收益', '利息以外淨損益', '各項提存', '稅前淨利', '稅後淨利', 
                                     '營業費用', '基本每股盈餘'],
                                 3: ['營業收入', '營業利益', '營業毛利', '營業成本', '營業費用',
                                     '營業外收入及支出', '稅前淨利', '稅後淨利', '基本每股盈餘'],
                                 4: ['利息淨收益', '利息以外淨收益', '淨收益', '稅前淨利', '稅後淨利', 
                                     '營業費用', '基本每股盈餘'],
                                 5: ['營業收入', '營業利益', '營業成本', '營業費用', '營業外收入及支出',
                                     '稅前淨利', '稅後淨利', '基本每股盈餘'],
                                 6: ['收入', '支出', '稅前淨利', '稅後淨利', '基本每股盈餘']}

        get_multiple_company_tables(
            args.target, config.profit_loss_col, company_columns_names, company_type)

    elif args.target == 'asset_debt':
        company_type = {1: 'bank', 3: 'standard',
                        4: 'holdings', 5: 'insurance'}
        company_column_names = {1: ['資產總額', '負債總額', '權益總額', '股本', '每股參考淨值'],
                                3: ['流動資產', '非流動資產', '資產總額', '流動負債', '非流動負債',
                                    '負債總額', '權益總額', '股本', '每股參考淨值'],
                                4: ['資產總額', '負債總額', '權益總額', '股本', '每股參考淨值'],
                                5: ['資產總額', '負債總額', '權益總額', '股本', '每股參考淨值']}

        get_multiple_company_tables(
            args.target, config.asset_debt_col, company_column_names, company_type)

    elif args.target == 'dividend':
        stocks = pd.read_csv('../data_sample/stock_meta_data.csv')['code']
        result = {}
        for stock_code in stocks:
            try:
                d = query_dividend(stock_code)
                result[stock_code] = d
            except:
                print(stock_code, 'fail')
        save('dividend.pkl', result)

    elif args.target == 'cashflow':
        get_cashflow_table(args.year, args.previous)

    elif args.target == 'price':
        get_historical_price()
