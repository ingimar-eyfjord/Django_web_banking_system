from django.db import models
from phonenumber_filed.modelfields import PhoneNumberField


class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True)
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
    phone_number = PhoneNumberField()

class Ledger(models.Model):
    account_id = models.ForeignKey(Account)
    amount = models.DecimalField(max_digits=225, decimal_places=2)
    transaction_date = models.DateTimeField.auto_now_add
    transaction_id = models.IntegerField(max_length=150)

class Account(models.Model):
    customer_id = models.ForeignKey(Customer)
    is_loan = models.BooleanField(False)

    @property
    def balance(self):
    return Ledger.object.filter(account_id=self).aggragate(Sum('amount'))

