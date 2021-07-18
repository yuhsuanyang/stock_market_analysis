from django.urls import path
from . import views

app_name = 'cashflow'
urlpatterns = [
    path('<stock_id>/cashflow', views.welcome, name="dashboard"),
]
