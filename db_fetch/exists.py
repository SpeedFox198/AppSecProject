"""
Existence Check Funcitons
-------------------------

Contains functions that checks for existence of value in database
"""
from .general import *


def _exists(table: str, **attributes) -> bool:
    """ Checks if attribute value pair exists in the table """

    # Can't check if exists if there's no attribute
    if not attributes:
        raise TypeError("Must check at least one attribute")

    # Return True non-empty tuple is return
    return bool(retrieve_db(table, **attributes))


def email_exists(email: str) -> bool:
    """ Checks if email exists """
    return _exists("Users", email=email)


def username_exists(username: str) -> bool:
    """ Checks if username exists """
    return _exists("Users", username=username)


def admin_exists() -> bool:
    """ Checks if admin account exists """
    return username_exists("admin")
