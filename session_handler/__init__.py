import pickle
from base64 import b64encode, b64decode

class UserSession:
    def __init__(self, user_id):
        self.user_id = user_id

def create_user_session(user_id):
    return b64encode(pickle.dumps(UserSession(user_id)))

def retrieve_user_session(session) -> UserSession:
    return pickle.loads(b64decode(session))
