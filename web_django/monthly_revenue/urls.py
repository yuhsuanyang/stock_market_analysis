from django.urls import path
from . import views

app_name = 'monthly_revenue'
urlpatterns = [path('<stock_id>/monthly_revenue', views.main, name='dashboard')]
