import pandas as pd
from pathlib import Path
from django.shortcuts import render
from .models import StockMetaData
# create data for overview dashboard

root = Path(__file__).resolve().parent
#print(root)  # ../meta_data

df = pd.read_csv(f"{root}/daily_report.csv")
with open(f"{root}/data_date_record.txt", "r") as f:
    last_date = f.read()

meta_data = StockMetaData.objects.all()


def make_ranking(sort_key, ascending=True):
    processed_df = df.sort_values(
        by=[sort_key, 'code'],
        ascending=[ascending, True]).iloc[0:50].reset_index(drop=True)
    processed_df['index'] = processed_df.index + 1
    processed_df['volume'] = round(processed_df['volume'], 3)
    processed_df = processed_df[[
        'index', 'code', 'today_close', 'updowns', 'fluctuation', 'volume'
    ]]
    #    return processed_df.values.tolist()
    result_list = []
    for sublist in processed_df.values.tolist():
        code = sublist[1].split(' ')[0]
        url = meta_data.filter(code=code)[0].get_price_url()
        result_list.append([sublist, url])
    print(result_list)
    return result_list


def get_tables(request):
    context = {
        'stock_list': meta_data,
        'date': last_date,
        'rise': make_ranking('fluctuation', False),
        'drop': make_ranking('fluctuation'),
        'volume': make_ranking('volume', False)
    }
    return render(request, 'overview_dashboard.html', context=context)
