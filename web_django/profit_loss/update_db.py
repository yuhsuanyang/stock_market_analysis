import argparse
import requests
import pandas as pd
from .models import *

url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'
company_columns = {
    1: [
        '利息淨收益', '利息以外淨損益', '呆帳費用、承諾及保證責任準備提存', '繼續營業單位稅前淨利（淨損）',
        '繼續營業單位本期稅後淨利（淨損）', '營業費用', '基本每股盈餘（元）'
    ],
    3: [
        '營業收入', '營業利益（損失）', '營業毛利（毛損）', '營業成本', '營業費用', '營業外收入及支出', '稅前淨利（淨損）',
        '本期淨利（淨損）', '基本每股盈餘（元）'
    ],
    4: [
        '利息淨收益', '利息以外淨收益', '淨收益', '繼續營業單位稅前損益', '本期稅後淨利（淨損）', '營業費用',
        '基本每股盈餘（元）'
    ],
    5: [
        '營業收入', '營業利益（損失）', '營業成本', '營業費用', '營業外收入及支出', '繼續營業單位稅前純益（純損）',
        '本期淨利（淨損）', '基本每股盈餘（元）'
    ],
    6: ['收入', '支出', '繼續營業單位稅前淨利（淨損）', '本期淨利（淨損）', '基本每股盈餘（元）']
}

company_columns_renames = {
    1: ['利息淨收益', '利息以外淨損益', '各項提存', '稅前淨利', '稅後淨利', '營業費用', '基本每股盈餘'],
    3: [
        '營業收入', '營業利益', '營業毛利', '營業成本', '營業費用', '營業外收入及支出', '稅前淨利', '稅後淨利',
        '基本每股盈餘'
    ],
    4: ['利息淨收益', '利息以外淨收益', '淨收益', '稅前淨利', '稅後淨利', '營業費用', '基本每股盈餘'],
    5: ['營業收入', '營業利益', '營業成本', '營業費用', '營業外收入及支出', '稅前淨利', '稅後淨利', '基本每股盈餘'],
    6: ['收入', '支出', '稅前淨利', '稅後淨利', '基本每股盈餘']
}

company_type = {
    1: 'bank',
    3: 'standard',
    4: 'holdings',
    5: 'insurance',
    6: 'other'
}


def crawl(year, season):
    dfs = {}
    form = {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK': 'sii',
        'year': year,
        'season': season,
    }
    r = requests.post(url, form)
    r.encoding = 'utf8'
    df = pd.read_html(r.text, header=None)
    for token in company_columns:
        print('   parsing', company_type[token])
        selected_columns = ['公司代號'] + company_columns[token]
        df[token].columns = [col.replace(' ', '') for col in df[token].columns]
        one_df = df[token][selected_columns]
        one_df.columns = ['code'] + company_columns_renames[token]
        dfs[token] = one_df.replace('--', 0)

    return dfs


def create_row(row, company_type, season):
    code = int(row['code'])
    if company_type == 'holdings':
        one_row = HoldingsProfitLossData(code=code,
                                         season=season,
                                         net_interest_income=row['利息淨收益'],
                                         net_noninterest_income=row['利息以外淨收益'],
                                         net_income=row['淨收益'],
                                         net_profit_before_tax=row['稅前淨利'],
                                         net_profit_after_tax=row['稅後淨利'],
                                         operation_expenses=row['營業費用'],
                                         EPS=row['基本每股盈餘'])

    elif company_type == 'bank':
        one_row = BankProfitLossData(code=code,
                                     season=season,
                                     net_interest_income=row['利息淨收益'],
                                     net_noninterest_income=row['利息以外淨損益'],
                                     deposits=row['各項提存'],
                                     net_profit_before_tax=row['稅前淨利'],
                                     net_profit_after_tax=row['稅後淨利'],
                                     operation_expenses=row['營業費用'],
                                     EPS=row['基本每股盈餘'])

    elif company_type == "insurance":
        one_row = InsuranceProfitLossData(code=code,
                                          season=season,
                                          business_income=row['營業收入'],
                                          business_interest=row['營業利益'],
                                          net_profit_before_tax=row['稅前淨利'],
                                          net_profit_after_tax=row['稅後淨利'],
                                          operation_expenses=row['營業費用'],
                                          operation_cost=row['營業成本'],
                                          non_operation_income=row['營業外收入及支出'],
                                          EPS=row['基本每股盈餘'])

    elif company_type == 'standard':
        one_row = StandardProfitLossData(code=code,
                                         season=season,
                                         business_income=row['營業收入'],
                                         business_interest=row['營業利益'],
                                         gross=row['營業毛利'],
                                         net_profit_before_tax=row['稅前淨利'],
                                         net_profit_after_tax=row['稅後淨利'],
                                         operation_expenses=row['營業費用'],
                                         operation_cost=row['營業成本'],
                                         non_operation_income=row['營業外收入及支出'],
                                         EPS=row['基本每股盈餘'])

    elif company_type == 'other':
        one_row = OtherProfitLossData(code=code,
                                      season=season,
                                      income=row['收入'],
                                      expenses=row['支出'],
                                      net_profit_before_tax=row['稅前淨利'],
                                      net_profit_after_tax=row['稅後淨利'],
                                      EPS=row['基本每股盈餘'])

    one_row.save()


def delete_data(year, season):
    BankProfitLossData.objects.filter(season=f"{year}_{season}").delete()
    StandardProfitLossData.objects.filter(season=f"{year}_{season}").delete()
    HoldingsProfitLossData.objects.filter(season=f"{year}_{season}").delete()
    InsuranceProfitLossData.objects.filter(season=f"{year}_{season}").delete()
    OtherProfitLossData.objects.filter(season=f"{year}_{season}").delete()


def main(action, year, season):
    if action == 'add_data':
        print('crawling....')
        dfs = crawl(year, season)
        for token in dfs:
            for i in range(len(dfs[token])):
                create_row(dfs[token].iloc[i], company_type[token],
                           f"{year}_{season}")
            print(company_type[token], f"{year} {season}", 'done')
    elif action == 'delete_data':
        delete_data(year, season)


if __name__ == "__name__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', type=str, default='add_data')
    parser.add_argument('--year', type=str, required=True)
    parser.add_argument('--season', type=str, required=True)
    args = parser.parse_args()
    main(args.action, args.year, args.season)
