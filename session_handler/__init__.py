import pickle
from base64 import b64encode, b64decode

class UserSession:
    def __init__(self, user_id:str) -> None:
        self.user_id = user_id

def create_user_session(user_id:str) -> bytes:
    return b64encode(pickle.dumps(UserSession(user_id)))

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
