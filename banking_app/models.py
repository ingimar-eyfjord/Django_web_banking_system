from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
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


class Account(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    is_loan = models.BooleanField(False)

    @property
    def balance(self):
<<<<<<< HEAD
        return Ledger.object.filter(account_id=self).aggregate(Sum('amount'))


class Ledger(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=225, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.IntegerField(max_length=150)

=======
        return Ledger.object.filter(account_id=self).aggragate(Sum('amount'))
>>>>>>> 1bad0a8 (whatever)

