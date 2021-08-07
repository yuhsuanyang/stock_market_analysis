from django.shortcuts import render, redirect
from django.urls import reverse
from dashboard_utils.common_functions import *
from .models import *
from meta_data.models import StockMetaData
from .util import create_dash
# Create your views here.

meta_data = StockMetaData.objects.all()


def get_posted_query(request):
    stock_id = request.POST['stock_id'].split(' ')[0]
    return redirect(
        reverse('asset_debt:dashboard', kwargs={'stock_id': stock_id}))


def get_raw_data(stock_id, company_type):
    if company_type in ['standard', 'other']:
        table = StandardAssetDebtData.objects.filter(code=stock_id)
    else:
        table = NonStandardAssetDebtData.objects.filter(code=stock_id)
    return create_df(table)


def welcome(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_raw_data(stock_id, info.company_type).astype(float)
    df['season'] = df['year'].astype(int).astype(
        str) + '_' + df['season'].astype(int).astype(str)
    del df['year']
    #    df = transform_by_season(df)
    print(df)
    app = create_dash(df)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    data['stock_info'] = info
    return render(request, 'asset_debt_dashboard.html', context=data)
