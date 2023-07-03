from django.test import TestCase
from price import models
# Create your tests here.

prices = models.PriceData.objects.all()
#stocks = PriceData.objects.values('code').distinct()

#class PriceTestCase(TestCase):
#    def test_price_data_amount(self):
#        print('hello world')

#       sample = models.PriceData(code=2330)
#       self.assertEqual(len(sample), 90)

#        for id_ in self.stocks:
#            price = self.prices.filter(code=id_)
#            self.assertEqual(len(price), 90)
