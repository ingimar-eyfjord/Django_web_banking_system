from django.db import models
from phonenumber_filed.modelfields import PhoneNumberField


class Customer(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    ranking = models.CharField(max_length=30)
    phone_number = PhoneNumberField()



class Account(models.Model):
    account_id = models.IntegerField(max_length=50)
    is_loan = models.BooleanField(False)
    username = models.CharField(max_length=150)


class Ledger(models.Model):
    credit = models.IntegerField(max_length=225)
    debit = models.IntegerField(max_length=225)
    transaction_date = models.DateTimeField.auto_now_add
    transaction_id = models.IntegerField(max_length=150)


