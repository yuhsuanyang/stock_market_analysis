from django.db import models
from dashboard_utils.terms import terms


# Create your models here.
class RevenueData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    year = models.IntegerField(help_text='年')
    month = models.IntegerField(help_text='月')
    revenue = models.FloatField(help_text='當月營收')
    month_increment = models.FloatField(help_text='上月比較增減%')
    year_increment = models.FloatField(help_text='去年比較增減%')

    def __str__(self):
        return f"{self.code} {self.year}_{self.month}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'year', 'month', 'revenue', 'month_increment',
                'year_increment'
        ]:
            col_dict[col] = terms[col]
        return col_dict

    def get_values(self):
        return {
            'revenue': self.revenue,
            'month_increment': self.month_increment,
            'year_increment': self.year_increment
        }
