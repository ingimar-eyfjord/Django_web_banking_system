import random
import os,binascii

def create_account_id():
    return str(random.randint(1000000000, 9999999999))

def create_transaction_id():
    return binascii.b2a_hex(os.urandom(15))
