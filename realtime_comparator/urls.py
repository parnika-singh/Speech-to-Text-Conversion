from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('realtime/', views.realtime_view, name='realtime'),
    path('future/', views.future_view, name='future'),
]