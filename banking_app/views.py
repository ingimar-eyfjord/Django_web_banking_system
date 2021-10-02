from typing import ContextManager
from django.shortcuts import render
from .models import Customer, Account
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    context = {
            'user' : "Ingimar"
              }
    return render(request, 'banking_templates/index.html', context)

@login_required
def user_account(request, pk):
    context = {
        'user' : "Ingimar"
            }
    return render(request, 'banking_templates/accounts.html', context)



@login_required
def staff_home(request):
        if request.user.is_staff:
            context = {
            "status": 200
            }
            return render(request, 'banking_templates/staff_home.html', context)
        else:
            context = {
            "status": 403
            }
            return render(request, 'banking_templates/index.html', context)

@login_required
def CreateAUser(request):
    context = {}
    if request.user.is_staff:
        if request.method == "POST":
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            username = request.POST['Username']
            firstName = request.POST['First_name']
            Last_name = request.POST['Last_name']
            email = request.POST['email']
            is_active = True
            last_login= now
            date_joined = now
            is_staff = False
            if password == confirm_password:
                if User.objects.create_user(username, email, password, is_active, last_login, date_joined, is_staff, firstName, Last_name):
                    return render(request, 'banking_templates/index.html', context)
                else:
                    context = {
                    'error' : 'Could not create user account - please try again.'
                    }
        else:
            context = {
                'error' : 'Passwords did not match - please try again'
                }
    return render(request, 'registration/staff_home.html', context)