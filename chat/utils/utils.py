import binascii
import os

def generate_key(size=20):
    return binascii.hexlify(os.urandom(size)).decode()
