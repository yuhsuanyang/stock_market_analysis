from django.urls import path
from . import views

app_name = 'dividend'
urlpatterns = [path('<stock_id>/dividend', views.main, name='dashboard')]
