from __future__ import annotations
import os
from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.db.models.deletion import PROTECT
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from .errors import InsufficientFunds
import random

BANK_NAME=os.environ['BANK_NAME']

class BankUID(models.Model):
    @classmethod
    @property
    def uid(cls):
        id = models.UUIDField(primary_key=True, editable=False)
        ids = cls.objects.all()
        newID = str(random.randint(4000, 5000))
        if len(ids) == 0:
            return cls.objects.create(id=newID)
        else:
            for id in ids:
                if newID != id:
                    return cls.objects.create(id=newID)
                else:
                    continue

    def __str__(self):
        return f'{self.pk}'

class AccountUID(models.Model):
    @classmethod
    @property
    def uid(cls):
        id = models.UUIDField(primary_key=True, editable=False)
        ids = cls.objects.all()
        newID = str(random.randint(40000, 50000))
        if len(ids) == 0:
            return cls.objects.create(id=newID)
        else:
            for id in ids:
                if newID != id:
                    return cls.objects.create(id=newID)
                else:
                    continue

    def __str__(self):
        return f'{self.pk}'


class UID(models.Model):
    @classmethod
    @property
    def uid(cls):
        return cls.objects.create()

    def __str__(self):
        return f'{self.pk}'

class Rank(models.Model):
    name = models.CharField(max_length=35, unique=True, db_index=True)
    value = models.IntegerField(unique=True, db_index=True)

    @classmethod
    def default_rank(cls) -> Rank:
        return cls.objects.all().aggregate(models.Min('value'))['value__min']

    def __str__(self):
        return f'{self.value}:{self.name}'

    

class Customer(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.PROTECT)
    rank = models.ForeignKey(Rank, default=2, on_delete=models.PROTECT)
    personal_id = models.IntegerField(db_index=True)
    phone = models.CharField(max_length=35, db_index=True)

    @property
    def full_name(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def accounts(self) -> QuerySet:
        return Account.objects.filter(user=self.user)

    @property
    def can_make_loan(self) -> bool:
        return self.rank.value >= settings.CUSTOMER_RANK_LOAN

    @property
    def default_account(self) -> Account:
        return Account.objects.filter(user=self.user).first()

    def make_loan(self, amount, name):
        assert self.can_make_loan, 'User rank does not allow for making loans.'
        assert amount >= 0, 'Negative amount not allowed for loan.'
        loan_account = AccountUID.uid
        loan = Account.objects.create(account_number=loan_account, user=self.user, name=f'Loan: {name}')
        bank = Banks.objects.get(bank_name=BANK_NAME)
        Ledger.transfer(
            amount,
            loan,
            bank,
            f'Loan paid out to account {self.default_account}',
            self.default_account,
            bank,
            f'Credit from loan {loan.pk}: {loan.name}',
            is_loan=True
        )

    @classmethod
    def search(cls, search_term):
        return cls.objects.filter(
            Q(user__username__contains=search_term) |
            Q(user__first_name__contains=search_term) |
            Q(user__last_name__contains=search_term) |
            Q(user__email__contains=search_term) |
            Q(personal_id__contains=search_term) |
            Q(phone__contains=search_term)
        )[:15]

    def __str__(self):
        return f'{self.personal_id}: {self.full_name}'

class Banks(models.Model):
    bank_number = models.OneToOneField(BankUID, primary_key=True, on_delete=models.PROTECT)
    bank_name = models.TextField()
    bank_ip_address = models.TextField()

    def __str__(self):
        return f'{self.bank_number} :|: {self.bank_name} :|: {self.bank_ip_address}'


class Account(models.Model):
    account_number = models.OneToOneField(AccountUID, primary_key=True, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=50, db_index=True)

    class Meta:
        get_latest_by = 'pk'

    @property
    def movements(self) -> QuerySet:
        return Ledger.objects.filter(account=self)

    @property
    def balance(self) -> Decimal:
        return self.movements.aggregate(models.Sum('amount'))['amount__sum'] or Decimal(0)

    def __str__(self):
        return f'{self.pk} :: {self.user} :: {self.name}'



class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    transaction = models.ForeignKey(UID, on_delete=models.PROTECT)
    bank_number = models.ForeignKey(Banks, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    text = models.TextField()
    ranking_choices = [
        ('P', 'Pending'),
        ('C', 'Completed'),
        ("F", 'Cancelled')
    ]
    status = models.CharField(
        max_length=15,
        choices=ranking_choices,
        default='C',
    )

    @classmethod
    def transfer(cls, amount, debit_account, bank_number_debit, debit_text, credit_account, bank_number_credit, credit_text, is_loan=False,**kwargs) -> int:
        assert amount >= 0, 'Negative amount not allowed for transfer.'
        with transaction.atomic():
            if debit_account.balance >= amount or is_loan:
                uid = UID.uid
                status = "C"
                if 'status' in kwargs:
                    status = kwargs.get('status')
                cls(amount=-amount, transaction=uid,
                    account=debit_account, text=debit_text, bank_number=bank_number_debit,status=status).save()
                cls(amount=amount, transaction=uid,
                    account=credit_account, text=credit_text,bank_number=bank_number_credit,status=status).save()
            else:
                raise InsufficientFunds
        return uid

    def __str__(self):
        return f'{self.amount} :|: {self.transaction} :|: {self.timestamp} :|: {self.account} :|: {self.text}'

class ExternalTransferMetaData(models.Model):
    transaction = models.ForeignKey(Ledger, on_delete=models.PROTECT)
    account = models.TextField()
    debit_account = models.TextField()
    external_bank_number = models.TextField()
    external_transaction_id = models.TextField()
    credit_text = models.TextField()

    @classmethod
    def log(self, transaction, credit_account, debit_account, external_transaction_id, credit_text, external_bank_number):
        self(transaction=transaction,
         account=credit_account, 
         external_bank_number=external_bank_number,
         debit_account=debit_account,
         external_transaction_id=external_transaction_id, 
         credit_text=credit_text).save()

    def __str__(self):
        return f'{self.transaction} :|: {self.account} :|: {self.debit_account} :|: {self.debit_bank} :|: {self.credit_text}'