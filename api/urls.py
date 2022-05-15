from django.urls import path
from bank import views


app_name = "api"

urlpatterns = [
    # path('transaction/receive/account/<int:pk>/ammount/<int>', views.ApiCreateTransaction.as_view()),
    # path('transaction/create/account/<int:pk>/ammount/<int>', views.ApiHandleTransaction.as_view()),
    path('transaction/create', views.ApiHandleTransaction.as_view()),
    path('transaction/confirm/<int>', views.ApiHandleTransaction.as_view()),
    path('transaction/cancel/<int>', views.ApiHandleTransaction.as_view()),
    path('account/<int:account_number>', views.ApiAccounts.as_view()),
]