from django.urls import path
from . import views

app_name = 'digitizer'

urlpatterns = [
    path('', views.index, name='index'),
]