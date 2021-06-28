from django.db import models
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

    def get_values(self):
        return {
            'open': self.Open,
            'high': self.High,
            'low': self.Low,
            'close': self.Close,
        }
