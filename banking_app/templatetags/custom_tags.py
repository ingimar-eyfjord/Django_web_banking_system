
from django import template

register = template.Library()

def currency(amount):
    balance = f"{float(amount):,}"
    return balance

register.filter('currency', currency)
# website for creating filters into the templates
# https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#:%7E:text=It%20also%20enables%20you%20to%20register%20tags%20without%20installing%20an%20application