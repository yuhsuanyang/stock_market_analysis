from django.urls import path

from . import views, simpleexample

app_name = 'price'
urlpatterns = [
    path('', views.get_posted_query, name="posted_query"),
    path('<stock_id>/price', views.main, name="dashboard"),
    path('try', views.try_dash, name="try")
]
