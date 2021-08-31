from django.urls import path
from . import views

app_name = 'similarity'
urlpatterns = [path('<stock_id>/similarity', views.main, name='dashboard')]
