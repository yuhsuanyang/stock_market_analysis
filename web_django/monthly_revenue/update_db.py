import requests
import pandas as pd
from io import StringIO
from .models import *

url_root = 'https://mops.twse.com.tw/nas/t21/sii/t21sc03_'
# cols = [('Unnamed: 0_level_0', '公司代號'), ('營業收入', '當月營收'),
#         ('營業收入', '上月比較增減(%)'), ('營業收入', '去年同月增減(%)')]
cols = ['公司代號', '當月營收', '上月比較增減(%)', '去年同月增減(%)']

def crawl(year, month):
    url = f"{url_root}{year}_{month}.html"
    print(url)
    res = requests.get(url)
    res.encoding = 'big5'
    dfs = pd.read_html(StringIO(res.text), encoding='big-5', attrs={'border': "5"})
    processed_dfs = []
    for i in range(len(dfs) - 1):
        dfs[i].columns = [col[1].replace(' ', '') for col in dfs[i].columns]
        processed_dfs.append(dfs[i][cols])
#         if ('Unnamed: 0_level_0', '公司代號') in dfs[i].columns:
#             one_df = dfs[i][cols]
#             one_df.columns = ['code', '當月營收', '上月比較增減(%)', '去年同月增減(%)']
#             processed_dfs.append(one_df)

    processed_dfs = pd.concat(processed_dfs, ignore_index=True)
    processed_dfs.rename(columns={'公司代號': 'code'}, inplace=True)
    total = processed_dfs[processed_dfs['code'] == '合計'].index
    data = processed_dfs.drop(total).fillna(0).reset_index(drop=True)
    return data


def create_row(row, year, month):
    code = int(row['code'])
    print(code)
    one_row = RevenueData(code=code,
                          year=year,
                          month=month,
                          revenue=row['當月營收'],
                          month_increment=row['上月比較增減(%)'],
                          year_increment=row['去年同月增減(%)'])
    one_row.save()


def delete_first_data(year):
    RevenueData.objects.filter(year=year).delete()


def main(year, month):
    # year: 民國年
    # month: 月(不加0)
    data = crawl(year, month)
    #    print(data)
    for i in range(len(data)):
        code = int(data.iloc[i]['code'])
        already_exists = RevenueData.objects.filter(code=code).filter(
            year=year).filter(month=month)
        if not len(already_exists):
            #            print(i)
            create_row(data.iloc[i], year, month)
