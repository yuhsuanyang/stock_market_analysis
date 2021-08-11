import pandas as pd
from pathlib import Path
from django.shortcuts import render
from .models import StockMetaData
# create data for overview dashboard

root = Path(__file__).resolve().parent
# print(root)  # ../meta_data

meta_data = StockMetaData.objects.all()


def make_ranking(df, sort_key, ascending=True, filter_PE=False):
    if filter_PE:
        processed_df = df[df.PE > 0]
    else:
        processed_df = df.copy()
    processed_df = processed_df.sort_values(
        by=[sort_key, 'code'],
        ascending=[ascending, True]).iloc[0:50].reset_index(drop=True)
    processed_df['index'] = processed_df.index + 1
    processed_df['volume'] = round(processed_df['volume'], 3)
    processed_df = processed_df[[
        'index', 'code', 'industry_type', 'today_close', 'updowns',
        'fluctuation', 'volume', 'PE'
    ]]
    #    return processed_df.values.tolist()
    result_list = []
    for sublist in processed_df.values.tolist():
        code = sublist[1].split(' ')[0]
        url = meta_data.filter(code=code)[0].get_price_url()
        result_list.append([sublist, url])


#    print(result_list)
    return result_list


def industry_ranking(df):
    df_industry = []
    for industry in df.industry_type.unique():
        data = df[df.industry_type == industry]
        ups = data[data.fluctuation > 0]
        downs = data[data.fluctuation < 0]
        df_industry.append([
            industry,
            round(data.fluctuation.mean(), 2),
            round(data.volume.mean(), 2),
            round(len(ups) / len(data), 2),
            round(len(downs) / len(data), 2)
        ])
    df_industry = pd.DataFrame(df_industry,
                               columns=[
                                   'industry_type', 'fluctuation', 'volume',
                                   'up_percentage', 'down_percentage'
                               ])
    df_industry = df_industry.sort_values(
        by=['fluctuation'], ascending=False).reset_index(drop=True)
    df_industry['index'] = df_industry.index + 1
    df_industry = df_industry[[
        'index', 'industry_type', 'fluctuation', 'volume', 'up_percentage',
        'down_percentage'
    ]]
    return df_industry.values.tolist()


def get_tables(request):
    df = pd.read_csv(f"{root}/daily_report.csv")
    with open(f"{root}/data_date_record.txt", "r") as f:
        last_date = f.read()

    df = df.dropna()
    context = {
        'stock_list': meta_data,
        'date': last_date,
        'rise': make_ranking(df, 'fluctuation', False),
        'drop': make_ranking(df, 'fluctuation'),
        'volume': make_ranking(df, 'volume', False),
        'PE': make_ranking(df, 'PE', filter_PE=True),
        'industry': industry_ranking(df)
    }
    return render(request, 'overview_dashboard.html', context=context)
