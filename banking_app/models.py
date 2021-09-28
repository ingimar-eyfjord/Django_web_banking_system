from django.db import models
from phonenumber_filed.modelfields import PhoneNumberField


class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    ranking = models.CharField(max_length=30)
    phone_number = PhoneNumberField()



