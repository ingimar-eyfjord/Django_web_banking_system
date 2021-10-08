from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import PositiveIntegerRelDbTypeMixin
from django.db.models.query_utils import select_related_descend
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import create_account_id, create_transaction_id


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
            return f'The phone number has been updated'
        except:
            return f'There was an error'

    # Show customer's details in admin page !!! but this also returns everything like this
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

    def open_account(user, is_loan, Amount):
        user = user
        account_id = create_account_id()
        new_account = Account(user=user, is_loan=False, account_id=account_id)
        new_account.save()
        if is_loan == True:
            loan_account_id = create_account_id()
            new_loan_account = Account(user=user, is_loan=True, account_id=loan_account_id)
            new_loan_account.save()
            Ledger.create_loan_transaction(loan_account_id, new_account, Amount)

    def balance(self):
        legderObject = Ledger.objects.filter(account=self)
        balance = 0
        for x in legderObject:
            balance = balance + x.amount
        return balance

        # return Ledger.objects.filter(account=self).aggregate(sum('amount'))

        # balance = Ledger.objects.filter(transaction_id="transaction_id").aggregate(sum('amount'))
        
        

    def get_transactions(self):
        legderObject = Ledger.objects.filter(transaction_id=self)
        transactions = []
        for x in legderObject:
            transaction = {
            'account_id': x.account_id,
            'ledger_amount': x.amount,
            'transaction_id': x.transaction_id,
            'transaction_date': x.transaction_date,
            }
            transactions.append(transaction)
        print()
        return transactions


    def __str__(self):
        return f"{self.account_id}" ### Changed this to only get the Account id because of the create loan / transactions

class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=225, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(
            max_length = 255,
            editable=False,
            )
 #transaction ID must not be uniques because there should be two of them 

    def create_transaction(PassedAmount, account_id, trans_id):
        transaction = Ledger(amount=PassedAmount, account=account_id, transaction_id=trans_id)
        transaction.save()
        
    def create_loan_transaction(debit_acc_id, credit_acc_id, amount):
        print(debit_acc_id, credit_acc_id)
        CreditToo = Account.objects.get(account_id=credit_acc_id)
        DebitFrom = Account.objects.get(account_id=debit_acc_id)
        amount_credit = float(amount)
        amount_debit = -float(amount)
        transaction_id = create_transaction_id()
        print("amounts herere", amount_credit, amount_debit)
        Ledger.create_transaction(amount_credit, CreditToo, transaction_id)
        Ledger.create_transaction(amount_debit, DebitFrom, transaction_id)
        
    def __str__(self):
        return f"{self.transaction_id}"