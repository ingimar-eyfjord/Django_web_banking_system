# Generated by Django 3.2.7 on 2022-01-05 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalTransferMetaData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_account', models.TextField()),
                ('credit_bank', models.TextField()),
                ('debit_account', models.TextField()),
                ('debit_bank', models.TextField()),
                ('credit_text', models.TextField()),
                ('debit_text', models.TextField()),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bank.ledger')),
            ],
        ),
    ]
