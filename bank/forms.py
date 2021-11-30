from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import Customer, Account, Banks


class TransferForm(forms.Form):
    amount  = forms.DecimalField(label='Amount', max_digits=10)
    debit_account = forms.ModelChoiceField(label='Your account', queryset=Customer.objects.none())
    debit_text = forms.CharField(label='Your description', max_length=25)
    bank_number = forms.ModelChoiceField(label='Recipient bank number', queryset=Banks.objects.all())
    credit_account = forms.IntegerField(label='Recipient account Number')
    credit_text = forms.CharField(label='Description for recipient', max_length=25)


    def clean(self):
        super().clean()

        # Ensure credit account exist
        credit_account = self.cleaned_data.get('credit_account')
        try:
            Account.objects.get(pk=credit_account)
        except ObjectDoesNotExist:
            self._errors['credit_account'] = self.error_class(['Credit account does not exist.'])

        # Ensure positive amount
        if self.cleaned_data.get('amount') < 0:
            self._errors['amount'] = self.error_class(['Amount must be positive.'])

        return self.cleaned_data


class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        super().clean()
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username):
            self._errors['username'] = self.error_class(['Username already exists.'])
        return self.cleaned_data


class UserForm(forms.ModelForm):
    username = forms.CharField(label='Username', disabled=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('rank', 'personal_id', 'phone')


class NewAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('name',)
