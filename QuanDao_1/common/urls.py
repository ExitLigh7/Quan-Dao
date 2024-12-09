from django.urls import path
from QuanDao_1.common.views import HomePage, search

urlpatterns = [
path('', HomePage.as_view(), name='home'),
path('search/', search, name='search'),
]