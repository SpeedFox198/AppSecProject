"""
Customer Functions
------------------

Contains functions that interacts with customer accounts
"""
from .general import *
from .user import retrieve_user 


""" Customer-triggered Functions """


def create_customer(user_id, username, email, password) -> None:
    """ Creates a new customer account in the database """

    # Insert user data into Users table
    insert_row("Users", (user_id, username, email, password, None, "customer"))
    # Insert customer details into Customers table
    insert_row("Customers", (user_id,), ("user_id",))

def create_2FA_token(user_id, twoFA_secret_token) -> None:
    """ Creates 2FA token for user_id """
    insert_row("twoFA", (user_id, twoFA_secret_token))

def retrieve_2FA_token(user_id: str) -> Union[tuple, None]:
    """ Retrieves 2FA token for user_id """
    return retrieve_db("twoFA", user_id=user_id, fetchone=True)

def delete_2FA_token(user_id: str) -> None:
    """ Deletes only the 2FA token from the Users database """
    delete_rows("twoFA", user_id=user_id)

def create_failed_login(username: str, attempt_no: str) -> None:
    """ Creates failed login entry """
    insert_row("FailedAttempts", (username, attempt_no))

def retrieve_failed_login(username: str) -> Union[tuple, None]:
    """ Retrieves and returns failed login from database """
    return retrieve_db("FailedAttempts", username=username, fetchone=True)

def update_failed_login(username: str, attempt_no: str) -> None:
    """ Updates failed login entry """
    update_rows("FailedAttempts", ("attempt_no",), (attempt_no,), username=username)

def delete_failed_logins(username: str) -> None:
    """ Deletes and returns failed login from database """
    delete_rows("FailedAttempts", username=username)

def create_lockout_time(user_id, date) -> None:
    """ Creates a timeout time """
    insert_row("Timeout", (user_id, date))

def retrieve_lockout_time(user_id: str) -> Union[tuple, None]:
    """ Retrieves and returns lockout time from database """
    return retrieve_db("Timeout", user_id=user_id, fetchone=True)

def delete_lockout_time(user_id: str) -> None:
    """ Deletes and returns lockout time from database """
    delete_rows("Timeout", user_id=user_id)

def retrieve_customer_details(user_id: str) -> Union[tuple, None]:
    """ Returns details of customer """
    return retrieve_db(
        "Customers",
        columns=("name", "credit_card_no", "address", "phone_no"),
        user_id=user_id,
        fetchone=True
    )

def create_otp(user_id: str, username: str, password: str, email: str, otp: str, otp_time: str) -> None:
    """ Creates OTP for temporary login """
    insert_row("OTP", (user_id, username, password, email, otp, otp_time))

""" Retrieves and returns OTP for all credentials """
def retrieve_otp(user_id: str) -> Union[tuple, None]:
    """ Retrieves and returns OTP for all credentials """
    return retrieve_db("OTP", user_id=user_id, fetchone=True)

def update_otp(user_id: str, username: str, password: str, email: str, otp: str, otp_time: str) -> None:
    """ Updates OTP for user_id """
    update_rows("OTP", ("username", "password", "email", "otp", "otp_time"), (username, password, email, otp, otp_time), user_id=user_id)

def delete_otp(user_id: str) -> Union[tuple, None]:
    """ Deletes and returns OTP from database """
    return delete_rows("OTP", user_id=user_id)

def update_customer_account(details1, details2):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """UPDATE Customers SET name = ?, phone_no = ? where user_id = ?;"""
    query2 = """UPDATE Users SET profile_pic = ? where user_id = ?;"""
    cur.execute(query, details1)
    cur.execute(query2, details2)
    con.commit()
    con.close()


def change_password(user_id: str, password: str) -> None:
    """ Updates user's password to new value """
    update_rows("Users", ("password",), (password,), user_id=user_id)


""" Admin-triggered Functions """


def retrieve_these_customers(limit:int, offset: int) -> list[tuple]:
    """ Retrieves and returns a list of max 10 customers starting from offset """
    return retrieve_db("Users NATURAL JOIN Customers", limit=limit, offset=offset, role="customer")

## TODO: name too similar to `retrieve_customer_details` function above ^ (curr line 24)
def retrieve_customer_detail(user_id: str):
    return retrieve_db("Users NATURAL JOIN Customers", fetchone=True, role="customer", or_and=1, user_id=user_id)


def number_of_customers() -> int:
    """ Returns count of number of customers """
    return retrieve_db("Customers", columns=("COUNT(*)",))[0][0]


def delete_customer(user_id: str) -> Union[tuple, None]:
    """ Deletes and returns customer from database """
    customer_data = retrieve_user(user_id)
    if customer_data:
        delete_rows("Users", user_id=user_id)
        delete_rows("Customers", user_id=user_id)
        return customer_data
