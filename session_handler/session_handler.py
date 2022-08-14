from pickle import dumps, loads
from base64 import b64encode, b64decode
from hmac import digest, compare_digest
from typing import Union, Any
from os import environ
import logging

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# File Handler
_LOG_FILE = "log/monitor_deserialisation.log"
_LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_fh = logging.FileHandler(_LOG_FILE)
_fh.setLevel(logging.WARNING)
_fh.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

logger.addHandler(_fh)

# Get secret key (you ain't gonna see it in plain text lol)
_SECRET_KEY = environ.get("VERY_SECRET_KEY")
assert _SECRET_KEY, "Secret key must be set in OS System environment variable"
_SECRET_KEY = _SECRET_KEY.encode()

# Character for separating session data and signature
_SEPARATOR = b"."
_DIGEST_METHOD = "sha512"
# TODO: add salt? (perhaps not? perhaps yes?)

def create_session(data) -> bytes:
    """ Creates and returns a regular session cookie """

    try:
        # Serialise data
        session = b64encode(dumps(data))
    except Exception as e:
        logger.critical(f"Error while serialising: {e}")
        logger.critical(f"Bad data: {data}")
        return b""
    else:
        # Generate signature
        signature = b64encode(digest(_SECRET_KEY, session, _DIGEST_METHOD))

        # Return session cookie
        return session + _SEPARATOR + signature


def retrieve_session(session:str) -> Union[Any, None]:
    """ Retrieve object from session cookie """

    if session:  # If session is not empty

        # Get session values (session and signature)
        try:
            values = session.encode().split(_SEPARATOR)
            a = digest(_SECRET_KEY, values[0], _DIGEST_METHOD)
            b = b64decode(values[-1])

        # If error occurs when comparing/decoding
        # Bad session was provided, return None
        except Exception as e:
            logger.warning(f"Invalid session: {session}")

        else:

            try:
                # Check for integrity of session
                if compare_digest(a, b):
                    # Returns user session object if session is valid
                    return loads(b64decode(values[0]))
                else:
                    logger.warning(f"Invalid session: {session}")
            except Exception as e:
                logger.critical(f"Error while deserialising: {e}")
                logger.critical(f"Malicious session: {session}")


def get_cookie_value(request, name:str) -> Union[Any, None]:
    """ Retrieve cookie with name from request """
    return retrieve_session(request.cookies.get(name))
