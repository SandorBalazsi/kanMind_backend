from django.contrib import admin
from django.urls import path
from .views import boards_view

urlpatterns = [
    path('', boards_view),
]