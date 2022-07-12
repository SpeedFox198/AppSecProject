from pickle import dumps, loads
from base64 import b64encode, b64decode
from hmac import digest, compare_digest
from typing import Union, Any
from os import environ

# Get secret key (you ain't gonna see it in plain text lol)
_SECRET_KEY = environ.get("VERY_SECRET_KEY").encode()
assert _SECRET_KEY, "Secret key must be set in OS System environment variable"

# Character for separating session data and signature
_SEPARATOR = b"."


def create_session(data) -> bytes:
    """ Creates and returns a regular session cookie """

    # Serialise data
    session = b64encode(dumps(data))

    # Generate signature
    signature = b64encode(digest(_SECRET_KEY, session, "sha256"))

    # Return session cookie
    return session + _SEPARATOR + signature


def retrieve_session(session:str) -> Union[Any, None]:
    """ Retrieve object from session cookie """

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
        except Exception as e:
            return None


def get_cookie_value(request, name:str) -> Union[Any, None]:
    """ Retrieve cookie with name from request """
    return retrieve_session(request.cookies.get(name))
