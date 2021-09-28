from django.db import models

# Create your models here.

class Account(models.Model):
    account_id = models.IntegerField(max_length=50)
    is_loan = models.BooleanField()
    username = models.CharField(max_length=150)
