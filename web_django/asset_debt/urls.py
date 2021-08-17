from django.urls import path
from . import views

app_name = 'asset_debt'
urlpatterns = [path('<stock_id>/asset_debt', views.main, name='dashboard')]
