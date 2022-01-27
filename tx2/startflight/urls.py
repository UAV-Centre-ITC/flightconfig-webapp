from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views


app_name = 'startflight'
urlpatterns = [
    path('', views.home_view, name='index')
]

urlpatterns += staticfiles_urlpatterns()
