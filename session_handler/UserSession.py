from datetime import datetime, timedelta
from typing import Union
from .session_handler import create_session as _cs, get_cookie_value as _gcv

SESSION_NAME = "user_session"

# Max duration user can stay logged in for (since last active)
_MAX_TIME = timedelta(hours=3)

class UserSession:
    """ Defines a user session """
    def __init__(self, user_id:str, is_admin:bool=False) -> None:
        self.user_id = user_id
        self.is_admin = is_admin
        self.last_active = datetime.now()

    def is_expired(self):
        """ Checks if session has expired (last active 3 hours ago) """
        return datetime.now() - self.last_active >= _MAX_TIME


def create_user_session(user_id:str, is_admin:bool=False) -> bytes:
    """ Creates and returns user session cookie """
    return _cs(UserSession(user_id, bool(is_admin)))


def retrieve_user_session(request) -> Union[UserSession, None]:
    """ Retrieve user session from request """
    return _gcv(request, SESSION_NAME)
