from django.urls import path
from bank import views


app_name = "api"

urlpatterns = [
    path('transaction/create/', views.Api_create_transaction.as_view()),
    path('transaction/receive/account/<int:pk>/ammount/<int>', views.Api_create_transaction.as_view()),
]