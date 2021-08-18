from django.db import models
from dashboard_utils.terms import terms

# Create your models here.


class DividendData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    year = models.IntegerField(help_text='年度')
    season = models.FloatField(help_text="季度")
    date = models.DateField(help_text="發放日期")
    cash = models.FloatField(help_text="現金股利")
    stock = models.FloatField(help_text="股票股利")

    def __str__(self):
        return f"{str(self.code)} {self.year} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in ['code', 'year', 'season']:
            col_dict[col] = terms[col]
        col_dict['date'] = '股利發放日期'
        col_dict['cash'] = '現金股利'
        col_dict['stock'] = '股票股利'
        return col_dict

    def get_values(self):
        return {
            'distribution_date': self.date,
            'cash_dividend': self.cash,
            'stock_dividend': self.stock,
        }
