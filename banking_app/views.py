from django.shortcuts import render
from .models import Customer, Account
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    return render(request, 'banking_app_templates/index.html', context)

@login_required
def user_account(request, pk):
    return render(request, 'banking_app_templates/accounts.html', context)

def signup(request):
    context = {}
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        username = request.POST['user']
        email = request.POST['email']
        is_active = True
        last_login= now
        date_joined = now
        is_staff = False
        if password == confirm_password:
            if User.objects.create_user(username, email, password, is_active, last_login, date_joined, is_staff):
                return render(request, 'banking_app_templates/index.html', context)
            else:
                context = {
                        'error' : 'Could not create user account - please try again.'
                        }
        else:
            context = {
                        'error' : 'Passwords did not match - please try again'
                        }

    return render(request, 'registration/signup.html', context)

@login_required
def staff_home(request, pk):
        if request.user.is_staff:
            return render(request, 'banking_app_templates/staff_home.html', context)
        else:
            return render(request, 'banking_app_templates/index.html', context)
