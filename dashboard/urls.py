from django.urls import path
from django.conf.urls import url
from .models import Estacao
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mapData/', views.data_map, name='mapData'),
    path('testando/', views.testando, name='testando'),
]
