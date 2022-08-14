import base64
from cryptography.fernet import Fernet
import os

AWS_KEY = b"NEqIjI1CsQfKQjJXITyC6tLOj_to_YOx-005CMwibVk="


def aws_encrypt(string):
    """Encryption will return a ciphertext"""
    key = AWS_KEY
    fernet = Fernet(key)

    encrypted = fernet.encrypt(string.encode())
    return encrypted.decode()


def aws_decrypt(ciphertext:bytes):
    """Decryption will return the plaintext string"""
    if isinstance(ciphertext, str):
        ciphertext = ciphertext.encode()
    if not isinstance(ciphertext, bytes):
        raise TypeError("ciphertext be bytes")
    key = AWS_KEY
    fernet = Fernet(key)

    decrypted = fernet.decrypt(ciphertext)
    return decrypted.decode()
