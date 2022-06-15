from pickle import dumps, loads
from base64 import b64encode, b64decode
from hmac import digest, compare_digest
from typing import Union
from os import environ

# Get secret key (you ain't gonna see it in plain text lol)
SECRET_KEY = environ.get("VERY_SECRET_KEY").encode()

# Character for separating session data and signature
SEPARATOR = b"."


class UserSession:
    def __init__(self, user_id:str, is_admin:bool=False) -> None:
        self.user_id = user_id
        self.is_admin = is_admin


def create_user_session(user_id:str, is_admin:bool=False) -> bytes:
    """ Creates and returns user session cookie """

    # Serialise user session object
    session = b64encode(dumps(UserSession(user_id, bool(is_admin))))

    # Generate signature
    signature = b64encode(digest(SECRET_KEY, session, "sha256"))

    # Return user session cookie
    return session + SEPARATOR + signature


def retrieve_user_session(session:bytes) -> Union[UserSession, None]:
    """ Retrieve user session object from session cookie """

    if session:  # If session is not empty

        # Get session values (session and signature)
        values = session.split(SEPARATOR)
        a = digest(SECRET_KEY, values[0], "sha256")
        b = b64decode(values[-1])

        # Check for integrity of session
        if compare_digest(a, b):

            # Returns user session object if session is valid
            return loads(b64decode(values[0]))
