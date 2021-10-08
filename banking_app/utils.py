import random
import os,binascii

def create_account_id():
    return str(random.randint(1000000000, 9999999999))

def create_transaction_id():
    return binascii.b2a_hex(os.urandom(15))

def return_transaction(parameter):
    transactions = []
    for x in parameter:
        transaction = {
            'account_id': x.account,
            'ledger_amount': float(x.amount),
            'transaction_id': x.transaction_id,
            'transaction_date': x.transaction_date,
            }
        transactions.append(transaction)
    return transactions
