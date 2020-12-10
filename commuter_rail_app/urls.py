from django.urls import path

from . import views

urlpatterns = [
    path('schedules', views.schedules),
    path('stations', views.stations),
]