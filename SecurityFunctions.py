import uuid
import os
import boto3
import base64
from argon2 import PasswordHasher

KEY_ID = '952ac3d9-9dc4-4322-8127-834c8a4fb54e'
AUTH_SIZE = 32

ph = PasswordHasher()

""" AES Encryption and Decryption using AWS KMS"""
def AWS_encrypt(plaintext):
    """ Encrypts plaintext and returns cipertext using AWS KMS"""

    session = boto3.session.Session(
        aws_access_key_id=os.environ.get('ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY'),
        region_name='ap-southeast-1'
    )

    client = session.client(
        service_name='kms'
    )

    # Encrypt
    encryption_result = client.encrypt(
        KeyId=KEY_ID,
        Plaintext=plaintext.encode("utf-8")
    )

    ciphertext_blob = encryption_result['CiphertextBlob']
    return base64.b64encode(ciphertext_blob)


def AWS_decrypt(ciphertext_blob):
    """ Decrypts ciphertext and returns plaintext using AWS KMS """

    session = boto3.session.Session(
        aws_access_key_id=os.environ.get('ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('SECRET_ACCESS_KEY'),
        region_name='ap-southeast-1'
    )

    client = session.client(
        service_name='kms'
    )

    # Decrypt
    decryption_result = client.decrypt(CiphertextBlob=ciphertext_blob)
    return decryption_result['Plaintext'].decode("utf-8")


""" UUID v5 for user id"""
def generate_uuid5(username):
    """ 
    Generates a UUID using a SHA-1 hash of a namespace UUID and a name
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, username))


""" UUID v4 for book id"""
def generate_uuid4():
    return str(uuid.uuid4())


""" Argon Hashing algorithm """
def pw_hash(pw):
    """ Returns a hashed password """
    return ph.hash(pw)


def pw_verify(hashed, pw):
    """ Returns True if password is valid """
    try:
        ph.verify(hashed, pw)
    except:
        return False

    return True


def pw_rehash(hashed, pw):
    """ Rehashes a password """
    if ph.check_needs_rehash(hashed):
        return ph.hash(pw)
