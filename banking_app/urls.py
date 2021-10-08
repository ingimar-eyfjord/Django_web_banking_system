from django.contrib import admin
from django.urls import path
from . import views

app_name = 'banking_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_user/', views.create_user, name='create_user'),
    path('my-accounts/<int:pk>/', views.user_account, name='my-accounts'),
    path('staff_home/', views.staff_home, name='staff_home'),
    path('all_customers/', views.all_customers, name='all_customers'),
    path('change_ranking/<int:pk>/', views.change_ranking, name='change_ranking'),
    path('create_account', views.create_account, name='create_account'),
    path('view_transactions/<int:pk>/', views.view_transactions, name='view_transactions'),
    ]

