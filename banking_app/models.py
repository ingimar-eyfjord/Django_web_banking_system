from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT)
    ranking_choices = [
        ('G', 'Gold'),
        ('S', 'Silver'),
        ('B', 'Basic'),
        ]
    ranking = models.CharField(
            max_length=15,
            choices=ranking_choices,
            default='B',
            )
    phone_number = models.CharField(max_length=20)

    @property
    def change_rank(self, pk, ranking):
        # TODO: add changing status
       try:
           self.objects.filter(pk=ranking_choices).update(ranking_choices=ranking)
           return f'The rank has been updated'
       except:
           return f'There was an error'

    # Show customer's details in admin page
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - username: {self.user.username}"


# Use signals to create a customer everytime a user is added
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()


class Account(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.PROTECT)
    is_loan = models.BooleanField(False)
    account_name = models.CharField(max_length=50)

    @property
    def balance(self):
        return Ledger.object.filter(account_id=self).aggregate(Sum('amount'))

    @property
    def get_transactions(self):
#   {make code to get all transactions maybe limit by 50 or something}
#   Entry.objects.all()[:10:2] =  transactions OFFSET 5 LIMIT 5 (current, limit = 5)
        return Ledger.object.filter(account_id=self)[:5]

class Ledger(models.Model):

    @property
    def create_transaction(self):
        account_id = models.ForeignKey(Account, on_delete=models.PROTECT)
        amount = models.DecimalField(max_digits=225, decimal_places=2)
        transaction_date = models.DateTimeField(auto_now_add=True)
        transaction_id = models.IntegerField(max_length=150)
#    {missing code for creating object (insert statment)}

