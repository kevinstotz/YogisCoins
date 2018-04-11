"""DimeCoins URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from DimeCoins.views import Index, CurrencyList, CurrencySearch, CurrencyLineChart, CurrencyDelta

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/currencylist/', CurrencyList.as_view(), name="currencyList"),
    path('api/currency/delta', CurrencyDelta.as_view(), name="currencyDelta"),
    path('api/currency/search', CurrencySearch.as_view(), name="currencySearch"),
    path('api/currency/linechart/<int:pk>/', CurrencyLineChart.as_view(), name="currencyLineChart"),
]

