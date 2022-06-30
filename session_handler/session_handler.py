from pickle import dumps, loads
from base64 import b64encode, b64decode
from hmac import digest, compare_digest
from datetime import datetime, timedelta
from typing import Union
from os import environ

# Get secret key (you ain't gonna see it in plain text lol)
_SECRET_KEY = environ.get("VERY_SECRET_KEY").encode()
assert _SECRET_KEY, "Secret key must be set in OS System environment variable"

# Character for separating session data and signature
_SEPARATOR = b"."

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

    # Serialise user session object
    session = b64encode(dumps(UserSession(user_id, bool(is_admin))))

    # Generate signature
    signature = b64encode(digest(_SECRET_KEY, session, "sha256"))

    # Return user session cookie
    return session + _SEPARATOR + signature


def retrieve_user_session(session:str) -> Union[UserSession, None]:
    """ Retrieve user session object from session cookie """

    if session:  # If session is not empty

        # Get session values (session and signature)
        try:
            values = session.encode().split(_SEPARATOR)
            a = digest(_SECRET_KEY, values[0], "sha256")
            b = b64decode(values[-1])

            # Check for integrity of session
            if compare_digest(a, b):

                # Returns user session object if session is valid
                return loads(b64decode(values[0]))

        # If error occurs when comparing/decoding
        # Bad session was provided, return None
        except Exception:
            return None