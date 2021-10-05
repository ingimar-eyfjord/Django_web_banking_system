from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_account_id

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

    def change_rank(pk, ranking):
        # TODO: add changing status
        try:

            Customer.objects.filter(pk=pk).update(ranking=ranking)
            print('The rank has been updated')
            return f'The rank has been updated'

        except:
            print('There was an error')
            return f'There was an error'

    def change_phone(pk, phone_number):
        # TODO: add changing status
        try:
            Customer.objects.filter(pk=pk).update(phone_number=phone_number)
            return f'The rank has been updated'
        except:
            return f'There was an error'

    # Show customer's details in admin page
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - username: {self.user.username}"

    # Use signals to create a customer everytime a user is added
    @receiver(post_save, sender=User)
    def create_customer(sender, instance, created, **kwargs):
        print("-------Hey--------", instance.pk)
        if created:
            Customer.objects.create(user=instance)

    #@receiver(post_save, sender=User)
    #def save_customer(sender, instance, **kwargs):
     #   instance.customer.save()


class Account(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.PROTECT)
    is_loan = models.BooleanField(False)
    account_id = models.CharField(
            max_length = 5,
            editable=False,
            unique=True,
            default=create_account_id
            )

    def open_account(user, is_loan, account_id):
        user = user
        account_id = account_id
        is_loan = is_loan
        new_account = Account(user=user, is_loan=is_loan, account_id=account_id)
        new_account.save()

    @property
    def balance(self):
        return Ledger.object.filter(account_id=self).aggregate(Sum('amount'))

    @property
    def get_transactions(self):
#   {make code to get all transactions maybe limit by 50 or something}
#   Entry.objects.all()[:10:2] =  transactions OFFSET 5 LIMIT 5 (current, limit = 5)
        return Ledger.object.filter(account_id=self)[:5]

    def __str__(self):
        return f"{self.account_id} - {self.user}"

class Ledger(models.Model):

    @property
    def create_transaction(self):
        account_id = models.ForeignKey(Account, on_delete=models.PROTECT)
        amount = models.DecimalField(max_digits=225, decimal_places=2)
        transaction_date = models.DateTimeField(auto_now_add=True)
        transaction_id = models.IntegerField(max_length=150)
#    {missing code for creating object (insert statment)}

