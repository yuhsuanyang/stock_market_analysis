"""web_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns and register namespace:  path('blog/', include('blog.urls')) 
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from meta_data.views import main
from meta_data.summary import get_tables

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('index/', main, name='index'),
    path('overview/', get_tables, name='overview'),
    path('analysis/', include('price.urls')),
    path('analysis/', include('profit_loss.urls')),
    path('analysis/', include('cashflow.urls')),
    path('analysis/', include('asset_debt.urls')),
    path('analysis/', include('dividend.urls')),
    path('analysis/', include('similarity.urls')),
    path('analysis/', include('monthly_revenue.urls')),
    path('analysis/', include('chip.urls')),
    path(
        'css/styles.css',
        TemplateView.as_view(template_name='styles.css',
                             content_type='text/css'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
