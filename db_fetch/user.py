"""
User Functions
--------------

Contains functions that interacts with users in database
(including both admin and customers)
"""
from .general import *


def user_auth(username: str, password: str) -> Union[tuple, None]:
    """ Authenticates password for username/email """
    return execute_db(
        """SELECT * FROM Users WHERE (username = ? OR email = ?) AND password = ?;""",
        (username, username, password),  # 2 usernames looks odd, but it's needed for username and email lol
        fetchone=True
    )

def retrieve_user(user_id: str) -> Union[tuple, None]:
    """ Returns user_data using user_id """
    return retrieve_db("Users", user_id=user_id, fetchone=True)
