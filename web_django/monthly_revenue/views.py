import pandas as pd
from django.shortcuts import render
from meta_data.models import StockMetaData
from .models import RevenueData
from .util import create_dash

# Create your views here.
meta_data = StockMetaData.objects.all()


def get_raw_data(stock_id):
    table = RevenueData.objects.filter(code=stock_id).order_by('year', 'month')
    cols = RevenueData.get_columns()
    cols = [cols[key] for key in cols]
    df = []
    for row in table:
        df.append([
            stock_id, row.year, row.month, row.revenue, row.month_increment,
            row.year_increment
        ])
    df = pd.DataFrame(df, columns=cols)
    return df


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_raw_data(stock_id)
    print(df)
    app = create_dash(df)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['stock_info'] = info
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    return render(request, 'monthly_revenue_dashboard.html', context=data)
