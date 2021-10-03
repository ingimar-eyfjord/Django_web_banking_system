from typing import ContextManager
from django.shortcuts import render
from .models import Customer, Account, Ledger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
from datetime import datetime

def index(request):
    user = request.user.username
    user_full_name = request.user.get_full_name()
    context = {
            'user_full_name': user_full_name
    }

    return render(request, 'banking_templates/index.html', context)

@login_required
def user_account(request, pk):
    context = {
            'user' : request.user.username
            }
    return render(request, 'banking_templates/user_account.html', context)

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
def create_user(request):
    context = {}
    if request.user.is_staff:
        if request.method == "POST":
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            is_active = True
            last_login= datetime.now()
            date_joined = date.today()
            is_staff = False
            if password == confirm_password:
                if User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'], is_active=is_active, last_login=last_login, date_joined=date_joined, is_staff=is_staff, first_name=request.POST['First_name'], last_name=request.POST['Last_name']):
                    context = {
                        "status": 200,
                        "message": "User has been successfully created"
                    }
                    return render(request, 'banking_templates/staff_home.html', context)
                else:
                    context = {
                    "status": 400,
                    'error' : 'Could not create user account - please try again.'
                    }
        else:
            context = {
                "status": 400,
                'error' : 'Passwords did not match - please try again'
                }
        return render(request, 'registration/staff_home.html', context)
    else:
        return render(request, 'registration/index.html', context)
