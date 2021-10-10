from typing import ContextManager
from django.shortcuts import render, get_object_or_404
from .models import Customer, Account, Ledger
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import date, datetime
from .utils import create_transaction_id
import secrets
from pprint import pprint


def index(request):
    user = request.user.username
    year = datetime.now().year
    context = {
        'user': user,
        'year': year
    }
    return render(request, 'banking_templates/index.html', context)


@login_required
def user_account(request, pk):
    user_accounts = Account.objects.filter(user=pk)
    customer_info = Customer.objects.get(user=pk)

    # this for loop finds and appends balance on the user account
    for x in user_accounts:
        print(x)
        x.balance = Account.balance(x)
    context = {
        'user': request.user.username,
        'user_accounts': user_accounts,
        'customer_info': customer_info
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
                    'error': 'Could not create user account - please try again.'
                }
        else:
            context = {
                "status": 400,
                'error': 'Passwords did not match - please try again'
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
    is_loan = False
    Amount = 0
    account_name = request.POST['account_name']

    if request.POST.get('loan', 0):
        is_loan = request.POST['loan']
    if request.POST.get('Amount', 0):
        Amount = request.POST['Amount']

     # Get all accounts of the current user
    accounts = Account.objects.filter(user=user)
    if accounts.count() == 0:
        account_name = "NemKonto"

    if is_loan == 'true':
        is_loan = True
        account_name = request.POST['loan_type']
    else:
        is_loan = False

    Account.open_account(user=user, account_name=account_name,
                         is_loan=is_loan, Amount=Amount)
    return HttpResponseRedirect(reverse('banking_app:staff_home'))


@ login_required
def change_ranking(request, pk):
    ranking = request.POST['Ranking']
    Customer.change_rank(pk, ranking)
    return HttpResponseRedirect(reverse('banking_app:all_customers'))


@ login_required
def view_transactions(request, pk):
    user_account = Account.objects.get(account_id=pk)
    # this for loop finds and appends balance on the user account
    get_context = Account.get_transactions(user_account)
    context = {'user_account': user_account, "balance": ""}
    context['balance'] = float(Account.balance(user_account))
    context['transactions'] = get_context[0]
    context['account'] = user_account
    context['direction'] = get_context[1]

    return render(request, 'banking_templates/view_transactions.html', context)


@ login_required
def make_transaction(request, pk):
    status = ''
    # Find the debit/from account
    DebitFrom = Account.objects.get(account_id=pk)
    # Current balance of the debit/from account
    current_balance = float(Account.balance(DebitFrom))

    if request.method == "POST":
        # Find the credit/to account
        current_account = request.POST.get('account_id')
        credit_to_acc = int(current_account[:11])
        CreditTo = Account.objects.get(account_id=credit_to_acc)

        # Find the account_owners
        user_debit = Customer.objects.select_related().get(user=DebitFrom.user)
        user_credit = Customer.objects.select_related().get(
            user=CreditTo.user)
        trans_id = create_transaction_id()

        # Convert transfer amount to float
        amount_credit = float(request.POST['Amount'])
        amount_debit = -float(request.POST['Amount'])

        Ledger.create_transaction(
            amount_credit, CreditTo, trans_id, user_credit)
        Ledger.create_transaction(
            amount_debit, DebitFrom, trans_id, user_debit)
        status = 'Success'
        print("success", status)
        return HttpResponseRedirect(reverse('banking_app:make_transaction', kwargs={'pk': pk}))

    context = {
        'account': int(pk),
        'accounts': Account.objects.exclude(pk=DebitFrom.pk),
        'balance': float(Account.balance(DebitFrom))
    }
    print(context)
    return render(request, 'banking_templates/make_transaction.html', context)
