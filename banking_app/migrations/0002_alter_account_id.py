# Generated by Django 3.2.7 on 2021-10-09 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
