from flask import make_response
import uuid

def generate_id():
    return str(uuid.uuid4())
