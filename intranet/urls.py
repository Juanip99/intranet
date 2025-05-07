from django.contrib import admin
from django.urls import path, include
from cartilla.views import index

urlpatterns = [
    path('intranet/', admin.site.urls),
    path('', index, name='index'),
    path('cartilla/', include('cartilla.urls')),
]