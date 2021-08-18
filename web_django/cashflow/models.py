from django.db import models
from dashboard_utils.terms import terms


# Create your models here.
class CashflowData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")  # year_season
    cash_from_operation = models.FloatField(help_text="營運現金流")
    cash_from_operation_activities = models.FloatField(help_text="營運淨現金流")
    real_estate = models.FloatField(help_text="資本支出")
    cash_from_investment = models.FloatField(help_text="投資淨現金流")
    cash_from_fundraise = models.FloatField(help_text="籌資淨現金流")

    def __str__(self):
        return f"{self.code} {self.season}"

    @staticmethod
    def get_columns():
        col_dict = {}
        for col in [
                'code', 'season', 'cash_from_operation',
                'cash_from_operation_activities', 'real_estate',
                'cash_from_investment', 'cash_from_fundraise'
        ]:
            col_dict[col] = terms[col]
        return col_dict

    def get_values(self):
        return {
            'cash_from_operation': self.cash_from_operation,
            'cash_from_operation_activities':
            self.cash_from_operation_activities,
            'real_estate': self.real_estate,
            'cash_from_investment': self.cash_from_investment,
            'cash_from_fundraise': self.cash_from_fundraise
        }
