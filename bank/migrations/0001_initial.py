# Generated by Django 3.2.7 on 2021-09-26 10:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=35, unique=True)),
                ('value', models.IntegerField(db_index=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UID',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Ledger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('text', models.TextField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bank.account')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='bank.uid')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personal_id', models.IntegerField(db_index=True)),
                ('first_name', models.CharField(db_index=True, max_length=50)),
                ('last_name', models.CharField(db_index=True, max_length=50)),
                ('phone', models.CharField(db_index=True, max_length=35)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'pk',
            },
        ),
    ]