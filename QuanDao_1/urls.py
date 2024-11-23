from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('QuanDao_1.common.urls')),
    path('academy/', include('QuanDao_1.academy.urls')),
]
