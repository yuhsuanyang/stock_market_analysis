from django.db import models


# Create your models here.
class StockMetaData(models.Model):
    code = models.CharField(max_length=4, primary_key=True, help_text='公司代碼')
    name = models.CharField(max_length=10, help_text='公司名稱')
    listed_date = models.CharField(max_length=10, help_text='上市日期')
    industry_type = models.CharField(max_length=20, help_text='產業類別')
    company_type = models.CharField(
        max_length=20, help_text='bank/standard/insurance/holdings/other')

    def __str__(self):
        return f"{self.code} {self.name}"


#    def get_absolute_url(self):
#        return reverse('meta_data')
