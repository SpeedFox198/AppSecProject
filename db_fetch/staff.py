from .general import *
from .user import retrieve_user


def create_staff(staff_id: str, username: str, email: str, password: str) -> None:
    """ Creates an admin account """
    insert_row("Users", (staff_id, username, email, password, None, "staff"))


def number_of_staff():
    return retrieve_db("Users", ["COUNT(*)"], role="staff")[0][0]


def retrieve_all_staff(limit:int, offset: int) -> list[tuple]:
    """ Retrieves and returns a list of max 10 customers starting from offset """
    return retrieve_db("Users", limit=limit, offset=offset, role="staff")


def delete_staff(staff_id):
    staff_data = retrieve_user(staff_id)
    if staff_data:
        delete_rows("Users", or_and=1, role="staff", user_id=staff_id)
        return staff_data
