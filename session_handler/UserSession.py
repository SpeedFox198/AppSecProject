from datetime import datetime, timedelta
from typing import Union
from .session_handler import create_session as _cs, get_cookie_value as _gcv

USER_SESSION_NAME = "user_session"
NEW_COOKIES = "new_cookies"
EXPIRED_COOKIES = "expired_cookies"

# Max duration user can stay logged in for (since last active)
_MAX_TIME = timedelta(hours=3)


class UserSession:
    """ Defines a user session """
    def __init__(self, user_id:str, role:str) -> None:
        self.user_id = user_id
        self.role = role
        self.last_active = datetime.now()

    def is_expired(self):
        """ Checks if session has expired (last active 3 hours ago) """
        return datetime.now() - self.last_active >= _MAX_TIME


def create_user_session(user_id:str, role:str) -> bytes:
    """ Creates and returns user session cookie """
    return _cs(UserSession(user_id, role))


def retrieve_user_session(request) -> Union[UserSession, None]:
    """ Retrieve user session from request """
    return _gcv(request, USER_SESSION_NAME)
