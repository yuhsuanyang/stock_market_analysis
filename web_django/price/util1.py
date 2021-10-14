import yfinance as yf
from datetime import datetime


def query_month_avg_price(stock_code, start_month, end_month):
    start_date = datetime.strptime(start_month, '%Y-%m')
    end_date = datetime.strptime(end_month, '%Y-%m')
    start_date = datetime.strftime(start_date, '%Y-%m-%d')
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    data = yf.download(f"{stock_code}.TW", start=start_date,
                       end=end_date)[['Close']]
    print(data)
    data['Month'] = [str(date)[0:7] for date in data.index]
    return data.groupby(['Month']).mean()


if __name__ == "__main__":
    stock_code = input('stock_code: ')
    start_month = input('start_month (YYYY-mm): ')
    end_month = input('end_month (YYYY-mm): ')
    result = query_month_avg_price(stock_code, start_month, end_month)
    print(result)
