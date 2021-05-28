import argparse
import pickle

import pandas as pd

import config

root = '../data_sample'


def merge(df_all, col_name):
    dfs, companies = [], []
    for i in df_all:
        if col_name in df_all[i].columns:
            dfs.append(df_all[i][col_name])
            companies.append(i)
    result = pd.concat(dfs, axis=1)
    result.columns = companies
    result = result.T
    result = result.reset_index()
    return result.rename(columns={'index': 'company'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str)
    parser.add_argument('--previous', default=False)
    args = parser.parse_args()
#    print(args)

    data = pickle.load(open(f'{root}/raw/{args.data}', 'rb'))
    for col in config.cashflow_col:
        file_name = config.cashflow_col[col]
        df = merge(data, col)
        if args.previous:
            previous_df = pd.read_csv(f'{root}/{file_name}.csv')
            df = df.merge(previous_df, on='company', how='right')
        print(df.columns)
        df.to_csv(f'{root}/{file_name}.csv', index=False)
