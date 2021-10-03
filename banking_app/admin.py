from django.contrib import admin
from .models import Customer, Account, Ledger
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Ledger)
