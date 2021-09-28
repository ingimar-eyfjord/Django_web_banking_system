from django.contrib import admin
from django.urls import path
from . import views

app_name = 'banking_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('my-accounts/<int:pk>/', views.user_account, name='user_account'),
    path('signup/', views.signup, name='signup'),
    path('staff_home.html', views.staff, name='staff'),
    ]
