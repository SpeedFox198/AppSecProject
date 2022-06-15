import pickle
from base64 import b64encode, b64decode
from hmac import digest, compare_digest
from itsdangerous import Signer

class UserSession:
    def __init__(self, user_id:str, is_admin:bool=False) -> None:
        self.user_id = user_id
        self.is_admin = is_admin

def create_user_session(user_id:str, is_admin:bool=False) -> bytes:
    return b64encode(pickle.dumps(UserSession(user_id, bool(is_admin))))

def retrieve_user_session(session:bytes) -> UserSession:

    # If no session
    if session is None:
        return
    
    # Check for integrity of session
    elif False:
        return

    # If session is valid
    else:
        return pickle.loads(b64decode(session))
