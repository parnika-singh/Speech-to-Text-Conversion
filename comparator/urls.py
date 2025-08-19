from django.urls import path
from . import views

app_name = 'comparator'

urlpatterns = [
    path('', views.index, name='index'),
    path('compare/', views.compare_audio, name='compare_audio'),
]