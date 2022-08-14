"""
Customer Functions
------------------

Contains functions that interacts with customer accounts
"""
from cmath import e
from .general import *
from .user import retrieve_user 
import datetime

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
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query1 = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """INSERT INTO FailedAttempts (user_id, attempts) VALUES (?, ?);"""
    user_id = cur.execute(query1, [username]).fetchone()
    # check if user_id exists
    if user_id is None:
        return None
    user_id = user_id[0]
    cur.execute(query2, [user_id, attempt_no])
    con.commit()
    con.close()

def retrieve_failed_login(username: str) -> Union[tuple, None]:
    """ Retrieves and returns failed login from database """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """SELECT * FROM FailedAttempts WHERE user_id = ?;"""
    user_id = cur.execute(query, [username]).fetchone()
    if user_id is None:
        return None
    user_id = user_id[0]
    failed_login_data = cur.execute(query2, [user_id]).fetchone()
    con.commit()
    con.close()
    return failed_login_data

def update_failed_login(username: str, attempt_no: str) -> None:
    """ Updates failed login entry """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query1 = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """UPDATE FailedAttempts SET attempts = ? WHERE user_id = ?;"""
    user_id = cur.execute(query1, [username]).fetchone()
    # check if user_id exists
    if user_id is None:
        return None
    user_id = user_id[0]
    cur.execute(query2, [attempt_no, user_id])
    con.commit()
    con.close()

def delete_failed_logins(username: str) -> None:
    """ Deletes and returns failed login from database """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """DELETE FROM FailedAttempts WHERE user_id = ?;"""
    user_id = cur.execute(query, [username]).fetchone()
    if user_id is None:
        return None
    user_id = user_id[0]
    cur.execute(query2, [user_id])
    con.commit()
    con.close()

def create_lockout_time(username, year, month, day, hour, minute, second) -> None:
    """ Creates a timeout time """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query1 = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """INSERT INTO Timeout (user_id, year, month, day, hour, minute, second) VALUES (?, ?, ?, ?, ?, ?, ?);"""
    user_id = cur.execute(query1, [username]).fetchone()
    # check if user_id exists
    if user_id is None:
        return None
    user_id = user_id[0]
    cur.execute(query2, [user_id, year, month, day, hour, minute, second])
    con.commit()
    con.close()

def retrieve_lockout_time(username: str) -> Union[tuple, None]:
    """ Retrieves and returns lockout time from database """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """SELECT * FROM Timeout WHERE user_id = ?;"""
    user_id = cur.execute(query, [username]).fetchone()
    if user_id is None:
        return None
    user_id = user_id[0]
    lockout_data = cur.execute(query2, [user_id]).fetchone()
    con.commit()
    con.close()
    return lockout_data

def delete_lockout_time(username: str) -> None:
    """ Deletes and returns lockout time from database """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """SELECT user_id FROM Users WHERE username = ?;"""
    query2 = """DELETE FROM Timeout WHERE user_id = ?;"""
    user_id = cur.execute(query, [username]).fetchone()
    if user_id is None:
        return None
    user_id = user_id[0]
    cur.execute(query2, [user_id])
    con.commit()
    con.close()

def retrieve_customer_details(user_id: str) -> Union[tuple, None]:
    """ Returns details of customer """
    return retrieve_db(
        "Customers",
        columns=("name", "credit_card_no", "address", "phone_no"),
        user_id=user_id,
        fetchone=True
    )

def create_otp(user_id, otp, year, month, day, hour, minute, second) -> None:
    """ Creates OTP for temporary login """
    insert_row("OTP", (user_id, otp, year, month, day, hour, minute, second))

""" Retrieves and returns OTP for all credentials """
def retrieve_otp(user_id) -> Union[tuple, None]:
    """ Retrieves and returns OTP for all credentials """
    return retrieve_db("OTP", user_id=user_id, fetchone=True)

def update_otp(user_id, otp, year, month, day, hour, minute, second) -> None:
    """ Updates OTP for user_id """
    update_rows("OTP", ("otp", "year", "month", "day", "hour", "minute", "second"), (otp, year, month, day, hour, minute, second), user_id=user_id)

def delete_otp(user_id) -> Union[tuple, None]:
    """ Deletes and returns OTP from database """
    return delete_rows("OTP", user_id=user_id)

def create_backup_codes(user_id, code1, code2, code3, code4, code5, code6) -> None:
    """ Creates backup codes for user_id """
    insert_row("BackUpCodes", (user_id, code1, code2, code3, code4, code5, code6))

def retrieve_backup_codes(user_id) -> Union[tuple, None]:
    """ Retrieves and returns backup codes for user_id """
    return retrieve_db("BackUpCodes", user_id=user_id, fetchone=True)

def delete_backup_codes(user_id) -> Union[tuple, None]:
    """ Deletes and returns backup codes for user_id """
    return delete_rows("BackUpCodes", user_id=user_id)

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