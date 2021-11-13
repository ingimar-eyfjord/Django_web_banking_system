from rest_framework import serializers
from .models import Ledger


class LedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ledger
        fields = '__all__'

    def rest_create_transaction(self, data):
        print(data)
        # transaction = Ledger(
        # )
        pass

    def rest_cancel_transaction(self, data):
        pass

    def rest_confirm_transaction(self, data):
        pass