import os
from decimal import Decimal
from pprint import pprint
from secrets import token_urlsafe
# from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from .forms import TransferForm, UserForm, CustomerForm, NewUserForm, NewAccountForm
from .models import Account, Ledger, Customer, UID, AccountUID, Banks, ExternalTransferMetaData
from .errors import InsufficientFunds
from api import serializers
from django.core import serializers as serialise
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import logout
import requests
from django.db import transaction

BANK_NAME=os.environ['BANK_NAME']

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('bank:index'))

@login_required
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('bank:staff_dashboard'))
    else:
        return HttpResponseRedirect(reverse('bank:dashboard'))


# Customer views
@login_required
def dashboard(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'
    accounts = request.user.customer.accounts
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank/dashboard.html', context)


@login_required
def account_details(request, pk):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    account = get_object_or_404(Account, user=request.user, pk=pk)
    context = {
        'account': account,
    }
    return render(request, 'bank/account_details.html', context)


@login_required
def transaction_details(request, transaction):
    movements = Ledger.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    context = {
        'movements': movements,
    }
    return render(request, 'bank/transaction_details.html', context)

@login_required
def transaction_external(request, transaction, credit, bank_number_credit, transactionID):
    movements = Ledger.objects.filter(transaction=transaction)
    if not request.user.is_staff:
        if not movements.filter(account__in=request.user.customer.accounts):
            raise PermissionDenied('Customer is not part of the transaction.')
    try:
        payload = {
            'username': 'PayLater',
            'password': '4%Z.%kTheA8GGh6'
        }
        url = f'http://{bank_number_credit.bank_ip_address}/api/v1/api-token-auth/'
        token_response = requests.post(url, data=payload)
        token = token_response.json()['token']
        PostUrl = f'http://{bank_number_credit.bank_ip_address}/api/v1/transaction/create'
        payload = {
            'account': request.POST['credit_account'],
            'debit_account': request.POST['debit_account'],
            'transaction': transactionID,
            'amount': request.POST['amount'],
            'text': request.POST['credit_text'],
             }
        headers = {'Authorization': token}
        response = requests.post(PostUrl, data=payload, headers=headers)
        response_JSON = token_response.json()
        if response.status_code == 200:
            context = {
            'status':200,
            'movements': movements,
            'to': credit,
            'response': response_JSON
            }
            movements.update(status="C")
            return render(request, 'bank/transaction_details_confirm.html', context)
        if response.status_code == 404:
            context = {
            'status':404,
            'movements': movements,
            'to': credit,
            }
            movements.update(status="F")
            return render(request, 'bank/transaction_details_confirm.html', context)
        else:
            context = {
            "status": 500,
            'movements': movements,
            'to': credit
            }
            movements.update(status="F")
            return render(request, 'bank/transaction_details_confirm.html', context)
    except requests.exceptions.InvalidSchema as e:
        context = {
        "status": 401,
        "text": e
        }
        movements.update(status="F")
        return render(request, 'bank/transaction_details_confirm.html', context)
    

@login_required
def make_transfer(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'
    if request.method == 'POST':
        form = TransferForm(request.POST)
        form.fields['debit_account'].queryset = request.user.customer.accounts
        if form.is_valid():
            amount = form.cleaned_data['amount']
            debit_account = Account.objects.get(pk=form.cleaned_data['debit_account'].pk)
            debit_text = form.cleaned_data['debit_text']
            bank_number_debit = Banks.objects.get(bank_name=BANK_NAME)
            bank_number_credit=form.cleaned_data['bank_number']
            bank2 = Banks.objects.get(pk=bank_number_credit)
            credit_text = form.cleaned_data['credit_text']
            if bank_number_debit == bank2:
                credit_account = Account.objects.get(pk=form.cleaned_data['credit_account'])
                status="C"
            else:
                credit_account = Account.objects.get(name="External_outgoing")
                status="P"
            try:
                transfer = Ledger.transfer(amount, debit_account, bank_number_debit, debit_text, credit_account, bank_number_credit, credit_text, status=status)
                if bank_number_debit != bank2:
                    return transaction_external(request, transfer, form.cleaned_data['credit_account'], bank_number_credit, transfer)
                else:
                    return transaction_details(request, transfer)

            except InsufficientFunds:
                    context = {
                        'title': 'Transfer Error',
                        'error': 'Insufficient funds for transfer.'
                    }
            return render(request, 'bank/error.html', context)
    else:
        form = TransferForm()
    form.fields['debit_account'].queryset = request.user.customer.accounts
    context = {
        'form': form,
    }
    return render(request, 'bank/make_transfer.html', context)


@login_required
def make_loan(request):
    assert not request.user.is_staff, 'Staff user routing customer view.'

    if not request.user.customer.can_make_loan:
        context = {
            'title': 'Create Loan Error',
            'error': 'Loan could not be completed.'
        }
        return render(request, 'bank/error.html', context)
    if request.method == 'POST':
        request.user.customer.make_loan(Decimal(request.POST['amount']), request.POST['name'])
        return HttpResponseRedirect(reverse('bank:dashboard'))
    return render(request, 'bank/make_loan.html', {})


# Staff views

@login_required
def staff_dashboard(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    return render(request, 'bank/staff_dashboard.html')


# @login_required
def staff_search_partial(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    search_term = request.POST['search_term']
    customers = Customer.search(search_term)
    context = {
        'customers': customers,
    }
    return render(request, 'bank/staff_search_partial.html', context)


@login_required
def staff_customer_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'GET':
        user_form = UserForm(instance=customer.user)
        customer_form = CustomerForm(instance=customer)
    elif request.method == 'POST':
        user_form = UserForm(request.POST, instance=customer.user)
        customer_form = CustomerForm(request.POST, instance=customer)
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
    new_account_form = NewAccountForm()
    context = {
        'customer': customer,
        'user_form': user_form,
        'customer_form': customer_form,
        'new_account_form': new_account_form,
    }
    return render(request, 'bank/staff_customer_details.html', context)


@login_required
def staff_account_list_partial(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    customer = get_object_or_404(Customer, pk=pk)
    accounts = customer.accounts
    context = {
        'accounts': accounts,
    }
    return render(request, 'bank/staff_account_list_partial.html', context)


@login_required
def staff_account_details(request, pk):
    assert request.user.is_staff, 'Customer user routing staff view.'

    account = get_object_or_404(Account, pk=pk)
    context = {
        'account': account,
    }
    return render(request, 'bank/account_details.html', context)


@login_required
def staff_new_account_partial(request, user):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_account_form = NewAccountForm(request.POST)
        if new_account_form.is_valid():
            account_num = AccountUID.uid
            Account.objects.create(account_number=account_num,user=User.objects.get(pk=user), name=new_account_form.cleaned_data['name'])
    return HttpResponseRedirect(reverse('bank:staff_customer_details', args=(user,)))


@login_required
def staff_new_customer(request):
    assert request.user.is_staff, 'Customer user routing staff view.'

    if request.method == 'POST':
        new_user_form = NewUserForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if new_user_form.is_valid() and customer_form.is_valid():
            username    = new_user_form.cleaned_data['username']
            first_name  = new_user_form.cleaned_data['first_name']
            last_name   = new_user_form.cleaned_data['last_name']
            email       = new_user_form.cleaned_data['email']
            password    = token_urlsafe(16)
            rank        = customer_form.cleaned_data['rank']
            personal_id = customer_form.cleaned_data['personal_id']
            phone       = customer_form.cleaned_data['phone']
            try:
                user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                )
                print(f'********** Username: {username} -- Password: {password}')
                Customer.objects.create(user=user, rank=rank, personal_id=personal_id, phone=phone)
                return staff_customer_details(request, user.pk)
            except IntegrityError:
                context = {
                    'title': 'Database Error',
                    'error': 'User could not be created.'
                }
                return render(request, 'bank/error.html', context)
    else:
        new_user_form = NewUserForm()
        customer_form = CustomerForm()
    context = {
        'new_user_form': new_user_form,
        'customer_form': customer_form,
    }
    return render(request, 'bank/staff_new_customer.html', context)

    # API view functions

class ApiCreateTransaction(generics.CreateAPIView):
    
    def post(self, request):
        uid = UID.uid
        request.data._mutable = True
        request.POST['transaction'] = uid.pk
        request.data._mutable = False
        # queryset = Ledger.objects.all()
        serializer_class = serializers.LedgerSerializer(data=request.data)
        if serializer_class.is_valid():
            # print(request)
            # serializer_class.save()
            # bankID = BankUID.uid
            return Response({"status": "success", "data": request.data}, status=status.HTTP_200_OK)

            # return Response({"status": "success", "data": serializer_class.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "error", "data": serializer_class.errors}, status=status.HTTP_400_BAD_REQUEST)


class ApiAccounts(generics.ListCreateAPIView):
    
    def get(self, request, account_number):
        try:
            queryset = User.objects.filter(account__account_number=account_number)
            data = {
                "first_name": queryset[0].first_name,
                "last_name": queryset[0].last_name,
            }
            # data = serialise.serialize("xml", data)
            return Response({"status": "success", "data": data}, status=status.HTTP_200_OK)
        except IntegrityError:
            context = {
                    'title': 'No account found',
                    'error': 'Account could not be found.'
                }
            # data = serialise.serialize("xml", context)
            return Response({"status": "error", "data": data}, status=status.HTTP_400_BAD_REQUEST)

class ApiHandleTransaction(APIView):
    
    def post(self, request):
        account = request.POST['account']
        credit_account = get_object_or_404(Account, pk=account) #makes sure account exists
        debit_bank = get_object_or_404(Banks, "PayLater") #?Need to get from authenticated user
        credit_bank = get_object_or_404(Banks, bank_name=BANK_NAME)
        serializer_class = serializers.LedgerSerializer(data=request.data)
        metadata_class = serializers.ExternalMetadataSerializers(data=request.data)
        if metadata_class.is_valid():
            if serializer_class.is_valid():
                uid = UID.uid
                debit_account = Account.objects.get(name="External_incoming")
                with transaction.atomic():
                    serializer_class.save(
                        transaction=uid, 
                        account=credit_account, 
                        bank_number=credit_bank)
                    serializer_class.save(
                        transaction=uid, 
                        account=debit_account, 
                        amount=-int(request.POST['amount']), 
                        bank_number=debit_bank)
                    ExternalTransferMetaData.objects.create(
                        transaction=uid,
                        credit_account=credit_account, 
                        debit_account=request.POST['debit_account'], 
                        external_transaction_id=request.POST['transaction'], 
                        credit_text=request.POST['credit_text'], 
                        external_bank_number=debit_bank)
                return Response({"status": "success", "data": serializer_class.data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "error", "data": serializer_class.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "error", "data": metadata_class.errors}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, *args, **kwargs):
        pass
    



# def api_transfers(request):
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
