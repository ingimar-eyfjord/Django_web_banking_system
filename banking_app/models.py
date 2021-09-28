from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):

    @property
    def create(self):
        user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
        ranking_choices = [
            ('G', 'Gold'),
            ('S', 'Silver'),
            ('B', 'Basic'),
            ]
        ranking = models.CharField(
                max_length=15,
                choices=ranking_choices,
                default='B',
                )
        phone_number = models.CharField(max_length=20)

    @property
    def change_rank(self):
   # {create code for changing rank}


class Account(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    is_loan = models.BooleanField(False)

    @property
    def balance(self):
        return Ledger.object.filter(account_id=self).aggregate(Sum('amount'))

    @property
    def create(self):
#        {create account create code here}

    @property
    def get_transactions(self):
#        {make code to get all transactions maybe limit by 50 or something}

class Ledger(models.Model):

    @property
    def create_transaction(self):
        account_id = models.ForeignKey(Account, on_delete=models.PROTECT)
        amount = models.DecimalField(max_digits=225, decimal_places=2)
        transaction_date = models.DateTimeField(auto_now_add=True)
        transaction_id = models.IntegerField(max_length=150)
#    {missing code for creating object (insert statment)}

