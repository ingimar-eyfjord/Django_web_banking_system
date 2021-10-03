from django.contrib import admin
from django.urls import path
from . import views

app_name = 'banking_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('my-accounts/<int:pk>/', views.user_account, name='my-accounts'),
    path('create_user/', views.create_user, name='create_user'),
    path('staff_home.html', views.staff_home, name='staff_home'),
    path('all_users.html', views.all_users, name='all_users'),
    ]
