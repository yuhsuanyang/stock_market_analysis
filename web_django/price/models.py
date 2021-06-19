from django.db import models
from django.urls import reverse
# Create your models here.


class PriceData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    Date = models.DateField(help_text="日期")
    Open = models.FloatField(help_text="開盤價")
    High = models.FloatField(help_text="最高價")
    Low = models.FloatField(help_text="最低價")
    Close = models.FloatField(help_text="收盤價")
    Volume = models.FloatField(help_text="成交量(股)")

    def __str__(self):
        return f"{str(self.code)} {self.Date}"

    def get_values(self):
        return {
            'open': self.Open,
            'high': self.High,
            'low': self.Low,
            'close': self.Close
        }
