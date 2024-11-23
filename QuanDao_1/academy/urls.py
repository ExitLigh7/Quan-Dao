from django.urls import path

from QuanDao_1.academy.views import AboutPage

urlpatterns = [
path('about/', AboutPage.as_view(), name='about'),
]