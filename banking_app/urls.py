from django.contrib import admin
from django.urls import path

from . import views

app_name = 'banking_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('my-account/<int:pk>/', views.user_account, name='user_account'),
]
