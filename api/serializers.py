from django.http import request
from rest_framework import serializers
from bank import models
from rest_framework.fields import CharField

class AccountSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Account
        fields = '__all__'

class ExternalMetadataSerializers(serializers.ModelSerializer):

    class Meta:
        model = models.ExternalTransferMetaData
        fields = ['account', 'debit_account', 'transaction', 'text', 'amount']

class LedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ledger
        fields = ['account', 'amount', 'text']
