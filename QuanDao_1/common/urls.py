from django.urls import path
from QuanDao_1.common.views import HomePage

urlpatterns = [
path('', HomePage.as_view(), name='home'),
]