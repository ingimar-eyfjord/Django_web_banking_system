from django.shortcuts import render
from .models import Customer, Accounts
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    return render(request, 'banking_app_templates/index.html', context)

@login_required
def user_account(request, pk):
    return render(request, 'banking_app_templates/accounts.html', context)
