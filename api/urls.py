from django.urls import path
from .views import BarChartDigitizerAPI

urlpatterns = [
    path('', BarChartDigitizerAPI.as_view(), name='digitize-api'),
]