from django.db import models

# Create your models here.


class NonStandardAssetDebtData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")  # year_season
    total_assets = models.FloatField(help_text="資產總額")
    total_debt = models.FloatField(help_text="負債總額")
    total_equity = models.FloatField(help_text="權益總額")
    share_capital = models.FloatField(help_text="股本")
    PBR = models.FloatField(help_text="每股參考淨值")

    def __str__(self):
        return f"{self.code} {self.season}"

    def get_values(self):
        return {
            'total_assets': self.total_assets,
            'total_debt': self.total_debt,
            'total_equity': self.total_equity,
            'share_capital': self.share_capital,
            'PBR': self.PBR
        }


class StandardAssetDebtData(models.Model):
    code = models.CharField(max_length=4, help_text="公司代碼")
    season = models.CharField(max_length=6, help_text="季度")  # year_season
    current_assets = models.FloatField(help_text="流動資產")
    noncurrent_assets = models.FloatField(help_text="非流動資產")
    total_assets = models.FloatField(help_text="資產總額")
    current_debt = models.FloatField(help_text="流動負債")
    noncurrent_debt = models.FloatField(help_text="非流動負債")
    total_debt = models.FloatField(help_text="負債總額")

    total_equity = models.FloatField(help_text="權益總額")
    share_capital = models.FloatField(help_text="股本")
    PBR = models.FloatField(help_text="每股參考淨值")

    def __str__(self):
        return f"{self.code} {self.season}"

    def get_values(self):
        return {
            'current_assets': self.current_assets,
            'noncurrent_assets': self.noncurrent_assets,
            'total_assets': self.total_assets,
            'current_debt': self.current_debt,
            'noncurrent_debt': self.noncurrent_debt,
            'total_debt': self.total_debt,
            'total_equity': self.total_equity,
            'share_capital': self.share_capital,
            'PBR': self.PBR
        }
