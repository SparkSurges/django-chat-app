import binascii
import os

def generate_key(size=20):
    return binascii.hexlify(os.urandom(size)).decode()

def generate_link():
    token = generate_key()
    link_data = {
        'created_at': datetime.now().isoformat(),
        'link': f'chat/{token}',
    }

    return link_data

