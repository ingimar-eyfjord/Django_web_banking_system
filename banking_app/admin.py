from django.contrib import admin
<<<<<<< HEAD
from django.contrib.auth.models import User

=======
from .models import Customer, Account, Ledger
>>>>>>> 6ffb920ab2e9602779976eb75074e6b5b2ba7d27

# Register your models here.
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Ledger)
