from django.shortcuts import render

from dashboard_utils.common_functions import *
from .models import *
from meta_data.models import StockMetaData
from .util import create_dash
# Create your views here.

meta_data = StockMetaData.objects.all()
table_dict = {
    'holdings': HoldingsProfitLossData,
    'bank': BankProfitLossData,
    'insurance': InsuranceProfitLossData,
    'standard': StandardProfitLossData
}



def get_raw_data(stock_id, company_type):
    table = table_dict[company_type].objects.filter(code=stock_id)
    return create_df(table)


def main(request, stock_id):
    info = meta_data.filter(code=stock_id)[0]
    same_trade = meta_data.filter(industry_type=info.industry_type)
    df = get_raw_data(stock_id, info.company_type).astype(float)
    #    print('------ before ------')
    #    print(df)
    df = transform_by_season(df)
    #    print('------ after ------')
    print(df)
    app = create_dash(df)
    data = {}
    data['stock_id'] = f"{stock_id} {info.name}"
    data['listed_date'] = info.listed_date
    data['industry_type'] = info.industry_type
    data['same_trade'] = same_trade
    data['stock_list'] = meta_data
    data['stock_info'] = info
    return render(request, 'profit_loss_dashboard.html', context=data)
