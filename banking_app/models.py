from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import PositiveIntegerRelDbTypeMixin
from django.db.models.query_utils import select_related_descend
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_account_id, create_transaction_id, return_transaction
from django.shortcuts import get_object_or_404


class Customer(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.PROTECT)
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
            return f'The phone number has been updated'
        except:
            return f'There was an error'

    # Show customer's details in admin page !!! but this also returns everything like this
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - username: {self.user.username}"

    # Use signals to create a customer everytime a user is added
    @receiver(post_save, sender=User)
    def create_customer(sender, instance, created, **kwargs):
        if created:
            Customer.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_customer(sender, instance, **kwargs):
     #   instance.customer.save()


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Customer, on_delete=models.PROTECT)
    account_name = models.CharField(max_length=30, editable=True)
    is_loan = models.BooleanField(False)
    account_id = models.CharField(
        max_length=5,
        editable=False,
        unique=True,
        default=create_account_id,
    )

    def open_account(user, is_loan, account_name, Amount):
        accounts = Account.objects.filter(user=user)
        new_account = Account(user=user, is_loan=is_loan,
                              account_name=account_name)
        new_account.save()
        if is_loan == True:
            print(new_account.account_id, accounts[0], Amount, user)
            # print(Ledger.create_loan_transaction())
            Ledger.create_loan_transaction(
                new_account.account_id, accounts[0], Amount, user)

    def balance(self):
        # This is not working, it says cannot aggregate sum string.
        # return Ledger.objects.filter(account=self).aggregate(sum('amount'))
        legderObject = Ledger.objects.filter(account=self)
        balance = 0
        for x in legderObject:
            balance = balance + x.amount
        return balance

    def get_transactions(self):
        legder = Ledger.objects.all().filter(account=self)
        transactions = []
        direction = []
        for x in legder:
            from_transaction = Ledger.objects.all().filter(transaction_id=x.transaction_id)
            from_transaction = return_transaction(from_transaction)
            transactions.append(from_transaction)
        return [transactions, direction]

    def __str__(self):
        # Changed this to only get the Account id because of the create loan / transactions
        return f"{self.account_id} - {self.user}"


class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=225, decimal_places=2)
    account_owner = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(
        max_length=255,
        editable=False,
    )
 # transaction ID must not be uniques because there should be two of them

    def create_transaction(PassedAmount, account_id, trans_id, account_owner):
        # add here check if balance is direction <= 0 if from
        transaction = Ledger(amount=PassedAmount, account=account_id,
                             transaction_id=trans_id, account_owner=account_owner)
        transaction.save()
    # Ledger.create_loan_transaction(new_account, Amount, user)

    def create_loan_transaction(debit_acc_id, CreditTo, amount, user):
        DebitFrom = Account.objects.get(account_id=debit_acc_id)
        amount_credit = float(amount)
        amount_debit = -float(amount)
        trans_id = create_transaction_id()
        Ledger.create_transaction(amount_credit, CreditTo, trans_id, user)
        Ledger.create_transaction(amount_debit, DebitFrom, trans_id, user)

    #account deposit
    def create_desposit(depositAmount, account_id, trans_id, account_owner):
        deposit = Ledger(amount=depositAmount, account=account_id, transaction_id=trans_id, account_owner=account_owner)
        transaction.save()

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_date}"
