from django.http import request
from rest_framework import serializers
from bank import models

class LedgerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ledger
        fields = '__all__'

    def rest_create_transaction(self, validated_data):
        print("api called")
        print(validated_data)
        # transaction = Ledger(
        # )

    def rest_cancel_transaction(self, data):
        pass

    def rest_confirm_transaction(self, data):
        pass