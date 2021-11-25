from django.urls import path
from . import views

app_name = 'chip'
urlpatterns = [
    path('<stock_id>/chip', views.main, name="dashboard"),
]
