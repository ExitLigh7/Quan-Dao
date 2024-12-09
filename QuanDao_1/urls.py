from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('qd_admin/', admin.site.urls),
    path('', include('QuanDao_1.common.urls')),
    path('academy/', include('QuanDao_1.academy.urls')),
    path('accounts/', include('QuanDao_1.accounts.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
