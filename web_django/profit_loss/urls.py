from django.urls import path
from . import views

app_name = 'profit_loss'
urlpatterns = [
    path('<stock_id>/profit_loss', views.main, name="dashboard"),
]
