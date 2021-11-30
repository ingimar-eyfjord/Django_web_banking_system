import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank.models import Account, Ledger, Customer, Banks, BankUID, AccountUID


class Command(BaseCommand):
    def handle(self, **options):
        print('Adding demo data ...')

        bank_user = User.objects.create_user('PayLater', email='', password=secrets.token_urlsafe(64))
        bank_user.is_active = False
        bank_user.save()

        ipo_number = AccountUID.uid
        ops_number = AccountUID.uid
        ext_in_num =AccountUID.uid
        ext_out_num = AccountUID.uid
        ipo_account = Account.objects.create(account_number=ipo_number,user=bank_user, name='Bank IPO Account')
        ops_account = Account.objects.create(account_number=ops_number, user=bank_user, name='Bank OPS Account')
        Account.objects.create(account_number=ext_out_num,user=bank_user, name='External_outgoing')
        Account.objects.create(account_number=ext_in_num,user=bank_user, name='External_incoming')
        bank_number = BankUID.uid
        bank = Banks.objects.create(bank_number=bank_number, bank_name = "PayLater", bank_ip_address="127.0.0.1:8000")

        Ledger.transfer(
            10_000_000,
            ipo_account,
            bank,
            'Operational Credit',
            ops_account,
            bank,
            'Operational Credit',
            is_loan=True,
        )

        dummy_user = User.objects.create_user('dummy', email='dummy@dummy.com', password='mirror12')
        dummy_user.first_name = 'Dummy'
        dummy_user.last_name  = 'Dimwit'
        dummy_user.save()
        dummy_customer = Customer(user=dummy_user, personal_id='555666', phone='555666')
        dummy_customer.save()
        check_num = AccountUID.uid
        dummy_account = Account.objects.create(account_number=check_num,user=dummy_user, name='Checking account')
        dummy_account.save()

        Ledger.transfer(
            1_000,
            ops_account,
            bank,
            'Payout to dummy',
            dummy_account,
            bank,
            'Payout from bank'
        )

        john_user = User.objects.create_user('john', email='john@smith.com', password='mirror12')
        john_user.first_name = 'John'
        john_user.last_name = 'Smith'
        john_user.save()
        john_customer = Customer.objects.create(user=john_user, personal_id='666777', phone='666777')
        john_customer.save()
        check_2_num = AccountUID.uid
        john_account = Account.objects.create(account_number=check_2_num,user=john_user, name='Checking account')
        john_account.save()
