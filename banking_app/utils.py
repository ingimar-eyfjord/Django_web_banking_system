import random
import os,binascii
def create_account_id():
    return str(random.randint(1000000000, 9999999999))

def create_transaction_id():
    return binascii.b2a_hex(os.urandom(15))

def return_transaction(parameter):
    transactions = []
    owner = ""
    for x in parameter:
        if float(x.amount) > 0:
            owner = x.debit.split('-')[0]
        else:
            owner = x.credit.split('-')[0]
        transaction = {
            'account_id': x.account,
            'ledger_amount': float(x.amount),
            'transaction_id': x.transaction_id,
            'transaction_date': x.transaction_date,
            'account_owner': x.account_owner.split('-')[0],
            'customer_view_owner': owner
            }
        transactions.append(transaction)
    return transactions
