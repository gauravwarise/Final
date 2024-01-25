from django.contrib import admin
from django.urls import path, include
from . views import *

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('stocktracker/', StockTracker.as_view(), name='stocktracker'),
    path('', HomeView.as_view(), name='home'),
]
