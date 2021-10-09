# Generated by Django 3.2.7 on 2021-10-09 12:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('banking_app', '0002_alter_account_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='account_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=30),
            preserve_default=False,
        ),
    ]