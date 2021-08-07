import argparse
import requests
import pandas as pd
from .models import *

url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb05'

company_columns = {
    'nonstandard':
    ['公司代號', '資產總額', '資產總計', '負債總額', '負債總計', '權益總額', '權益總計', '股本', '每股參考淨值']
}
company_columns['standard'] = company_columns['nonstandard'] + [
    '流動資產', '非流動資產', '流動負債', '非流動負債'
]

company_columns_renames = {
    'nonstandard': ['資產總額', '負債總額', '權益總額', '股本', '每股參考淨值']
}
company_columns_renames['standard'] = company_columns_renames[
    'nonstandard'] + ['流動資產', '非流動資產', '流動負債', '非流動負債']

company_type = {1: 'bank', 3: 'standard', 4: 'holdings', 5: 'insurance'}


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
    for token in company_type:
        print('   parsing', company_type[token])
        if company_type[token] == 'standard':
            candidate_columns = company_columns['standard']
            renamed_columns = company_columns_renames['standard']
        else:
            candidate_columns = company_columns['nonstandard']
            renamed_columns = company_columns_renames['nonstandard']
        selected_columns = [
            col for col in candidate_columns if col in df[token].columns
        ]
        one_df = df[token][selected_columns]
        one_df.columns = ['code'] + renamed_columns
        dfs[token] = one_df

    return dfs


def create_row(row, company_type, season):
    code = int(row['code'])
    if company_type == 'standard':
        one_row = StandardAssetDebtData(code=code,
                                        season=season,
                                        current_assets=row['流動資產'],
                                        noncurrent_assets=row['非流動資產'],
                                        total_assets=row['資產總額'],
                                        current_debt=row['流動負債'],
                                        noncurrent_debt=row['非流動負債'],
                                        total_debt=row['負債總額'],
                                        total_equity=row['權益總額'],
                                        share_capital=row['股本'],
                                        PBR=row['每股參考淨值'])

    else:
        one_row = NonStandardAssetDebtData(code=code,
                                           season=season,
                                           total_assets=row['資產總額'],
                                           total_debt=row['負債總額'],
                                           total_equity=row['權益總額'],
                                           share_capital=row['股本'],
                                           PBR=row['每股參考淨值'])
    one_row.save()


def delete_data(year, season):
    NonStandardAssetDebtData.objects.filter(season=f"{year}_{season}").delete()
    StandardAssetDebtData.objects.filter(season=f"{year}_{season}").delete()


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
