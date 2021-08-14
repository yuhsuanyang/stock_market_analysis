from django.db import models

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

    def get_values(self):
        return {
            'distribution_date': self.date,
            'cash_dividend': self.cash,
            'stock_dividend': self.stock,
        }
