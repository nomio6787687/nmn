from django.contrib import admin
from django.urls import path
from .views import checkService

urlpatterns = [
    path('gettime/', checkService, name='checkService'),
]