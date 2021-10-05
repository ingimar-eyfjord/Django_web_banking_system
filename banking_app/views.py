from typing import ContextManager
from django.shortcuts import render, get_object_or_404
from .models import Customer, Account, Ledger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
from datetime import datetime
import secrets
from .utils import create_account_id


def index(request):
    user = request.user.username
    #user_full_name = request.user.get_full_name()
    context = {
            'user': user,
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
            all_users = User.objects.all().filter(is_staff=False)[:15]
            all_customers = Customer.objects.all()[:15]

            context = {
            "status": 200,
            'all_users': all_users,
            'all_customers': all_customers
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
            # From create_user form
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            # Setting the following automatically for new user/customer
            is_active = True
            last_login = datetime.now()
            date_joined = date.today()
            is_staff = False
            phone_number = request.POST['phone_number']
            ranking = request.POST['ranking']
        if password == confirm_password:
                if User.objects.create_user(username, email, password, first_name=request.POST['first_name'], last_name=request.POST['last_name'], is_active=is_active, last_login=last_login, date_joined=date_joined, is_staff=is_staff):
                    context = {
                        "status": 200,
                        "message": "User has been successfully created"
                    }
                    user_id = User.objects.last()
                    Customer.change_rank(user_id, ranking)
                    Customer.change_phone(user_id, phone_number)
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
        return render(request, 'banking_templates/staff_home.html', context)
    else:
        return render(request, 'banking_templates/index.html', context)

@login_required
def all_customers(request):
    all_users = User.objects.all().filter(is_staff=False)[:15]
    all_customers = Customer.objects.all()[:15]
    all_accounts = Account.objects.all().select_related('user')

    number_of_accounts = 5
    account_list = []
    for i in range(number_of_accounts):
        account = Account()
        account_list.append(account)

    context = {
            'all_users': all_users,
            'all_customers': all_customers,
            'all_accounts': all_accounts
            }
    return render(request, 'banking_templates/all_customers.html', context)

@login_required
def create_account(request):
    pk = request.POST['pk']
    user = get_object_or_404(Customer, pk=pk)
    is_loan = request.POST['loan']
    if is_loan == 'true':
        is_loan = True
    else:
        is_loan = False
    hexstr = secrets.token_hex(4)
    #account_id = int(hexstr, 16)
    account_id = create_account_id()
    Account.open_account(user=user, is_loan=is_loan, account_id=account_id)
    return HttpResponseRedirect(reverse('banking_app:all_customers'))


@login_required
def change_ranking(request, pk):
    ranking = request.POST['ranking']
    print("-----------HEY ---", ranking, pk)
    Customer.change_rank(pk, ranking)
    # customer = get_object_or_404(Customer, pk=pk)
    # if "selected" in request.POST:
    #     customer.ranking = new_ranking
    # customer.save()
    return HttpResponseRedirect(reverse('banking_app:all_customers'))
