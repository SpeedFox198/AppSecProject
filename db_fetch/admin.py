"""
Admin Functions
---------------

Contains functions that interacts with admin account
"""
from .general import *


def create_admin(admin_id: str, username: str, email: str, password: str) -> None:
    """ Creates an admin account """
    insert_row("Users", (admin_id, username, email, password, None, "admin"))
