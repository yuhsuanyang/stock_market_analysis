from django.db import models
from dashboard_utils.terms import terms
# Create your models here.


class PriceData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    date = models.DateField(help_text="日期")
    key = models.CharField(max_length=30,
                           primary_key=True,
                           help_text="code YYYY-MM-DD")
    Open = models.FloatField(help_text="開盤價")
    High = models.FloatField(help_text="最高價")
    Low = models.FloatField(help_text="最低價")
    Close = models.FloatField(help_text="收盤價")
    Volume = models.FloatField(help_text="成交量(股)")
    PE = models.FloatField(help_text="本益比")

    def __str__(self):
        return f"{str(self.code)} {self.date}"

    @staticmethod
    def get_columns():
        return {
            'code': '公司代碼',
            'date': '日期',
            'Open': '開盤價',
            'High': '最高價',
            'Low': '最低價',
            'Close': '收盤價',
            'Volume': '成交量（股）',
            'PE': '本益比'
        }

    def get_values(self):
        return {
            'open': self.Open,
            'high': self.High,
            'low': self.Low,
            'close': self.Close,
        }


class InstitutionalInvestorData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    date = models.DateField(help_text="日期")
    key = models.CharField(max_length=30,
                           primary_key=True,
                           help_text="code YYYY-MM-DD")
    foreign_buy = models.FloatField(help_text="外資買進股數")
    foreign_sell = models.FloatField(help_text="外資賣出股數")
    invest_buy = models.FloatField(help_text="投信買進股數")
    invest_sell = models.FloatField(help_text="投信賣出股數")
    dealer_buy = models.FloatField(help_text="自營商買進股數")
    dealer_sell = models.FloatField(help_text="自營商賣出股數")

    def __str__(self):
        return f"{str(self.code)} {self.date}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'date', 'foreign_buy', 'foreign_sell', 'invest_buy',
                'invest_sell', 'dealer_buy', 'dealer_sell'
        ]:
            col_dict[col] = terms[col]
        return col_dict

    def get_values(self):
        return {
            'foreign_buy': self.foreign_buy,
            'foreign_sell': self.foreign_sell,
            'invest_buy': self.invest_buy,
            'invest_sell': self.invest_sell,
            'dealer_buy': self.dealer_buy,
            'dealer_sell': self.dealer_sell
        }
