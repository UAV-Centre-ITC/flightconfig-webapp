from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'monitor'

urlpatterns = [
    path('<slug:flightname>/', views.monitoring_view, name='monitoring_view')
]

urlpatterns += staticfiles_urlpatterns()
