# Generated by Django 3.2.8 on 2021-10-09 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking_app', '0007_rename_account_owner_ledger_account_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ledger',
            old_name='Account_owner',
            new_name='account_owner',
        ),
    ]