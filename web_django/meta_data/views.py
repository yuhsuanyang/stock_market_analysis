import json
import time
import requests
from django.shortcuts import render
from datetime import datetime, timedelta

# Create your views here.


def get_latest_data():
    ref_date = datetime.today() - timedelta(days=0)
    if ref_date.isoweekday() == 6:
        adjust = 0
    elif ref_date.isoweekday() == 7:
        adjust = -1
    else:
        adjust = 1
    today = ref_date + timedelta(days=adjust)
    yesterday = today - timedelta(days=2)
    print(datetime.strftime(ref_date, '%Y-%m-%d'))
    #    print(today, today.isoweekday())
    #    print(yesterday, yesterday.isoweekday())
    start_date = datetime.strftime(yesterday, '%Y-%m-%d')
    end_date = datetime.strftime(today, '%Y-%m-%d')
    start = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
    end = int(time.mktime(time.strptime(end_date, '%Y-%m-%d')))

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/%5ETWII?period1={start}&period2={end}&interval=1d&events=history&=hP2rOschxO0"
    res = requests.get(url)
    data = json.loads(res.text)
    data = data['chart']['result'][0]['indicators']['quote'][0]
    print(data)
    return {
        'date': datetime.strftime(ref_date, '%Y-%m-%d'),
        'yesterday_close': round(data['close'][0], 2),
        'today_close': round(data['close'][1], 2),
        'low': round(data['low'][1], 2),
        'high': round(data['high'][1], 2),
        'open': round(data['open'][1], 2)
    }


#    return pd.read_csv(StringIO(res.text))
def news(request):
    data = get_latest_data()
    if data['today_close'] > data['yesterday_close']:
        trend = 'red'
    elif data['today_close'] < data['yesterday_close']:
        trend = 'green'
    else:
        trend = 'gold'
    data['trend'] = trend
    print(data)
    return render(request, 'index.html', context=data)


if __name__ == "__main__":
    get_latest_data()
