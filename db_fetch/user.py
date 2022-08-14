"""
User Functions
--------------

Contains functions that interacts with users in database
(including both admin and customers)
"""
from .general import *


def retrieve_password(user_id: str) -> Union[str, None]:
    """ Returns the hashed password for user with user_id """
    password = retrieve_db("Users", columns=["password"], user_id=user_id, fetchone=True)
    if password:
        return password[0]

def retrieve_user_ids_and_emails() -> list[tuple[str, str]]:
    """ Returns list of all userids and emails in database """
    return retrieve_db("Users", columns=["user_id", "email"])


def retrieve_user(user_id: str) -> Union[tuple, None]:
    """ Returns user_data using user_id """
    return retrieve_db("Users", user_id=user_id, fetchone=True)


def retrieve_user_id(email: str) -> Union[str, None]:
    """ Returns user_id using email """
    data:tuple = retrieve_db("Users", columns=["user_id"], email=email, fetchone=True)
    if data:
        return data[0]

def retrieve_user_by_username(username: str) -> Union[str, None]:
    """ Returns user_id using username """
    data = retrieve_db("Users",username=username, fetchone=True)
    if data:
        return data[0]

def retrieve_email_by_username(username: str) -> Union[str, None]:
    """ Returns email using username """
    data = retrieve_db("Users",username=username, fetchone=True)
    if data:
        return data[2]

def retrieve_username_by_user_id(user_id: str) -> Union[str, None]:
    """ Returns username using user_id """
    data = retrieve_db("Users",user_id=user_id, fetchone=True)
    if data:
        return data[1]