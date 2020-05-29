"""Utilities for Dyson Pure Hot+Cool link devices."""
import json
import base64
import hashlib
from Crypto.Cipher import AES

def printable_fields(fields):
    """Return printable fields.

    :param fields list of tuble with (label, vallue)
    """
    for field in fields:
        yield field[0]+"="+field[1]

def unpad(string):
    """Un pad string."""
    return string[:-ord(string[len(string) - 1:])]

def decrypt_password(encrypted_password):
    """Decrypt password.

    :param encrypted_password: Encrypted password
    """
    key = b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10' \
          b'\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f '
    init_vector = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                  b'\x00\x00\x00\x00'
    cipher = AES.new(key, AES.MODE_CBC, init_vector)
    json_password = json.loads(unpad(
        cipher.decrypt(base64.b64decode(encrypted_password)).decode('utf-8')))
    return json_password["apPasswordHash"]

def hash_password(hashed_password):
    """Hash password (found in manual) to a base64 encoded of its shad512 value"""
    hashp = hashlib.sha512()
    hashp.update(hashed_password.encode('utf-8'))
    return base64.b64encode(hashp.digest()).decode('utf-8')

def get_field_value(state, field):
    """Get field value."""
    return state[field][1] if isinstance(state[field], list) else state[
        field]
