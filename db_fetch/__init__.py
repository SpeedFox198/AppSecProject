from contextlib import closing
import sqlite3

DATABASE = r"database.db"


def execute_db(sql: str, parameters):
    with closing(sqlite3.connect(DATABASE)) as con:
        with con:
            cur = con.cursor()
            data = cur.execute(sql, parameters).fetchall()
            return data


# def create_user(user):
#     execute_db(
#         """INSERT INTO Users VALUES (?, ?, ?, ?, NULL, ?)""",
#         (user.id, user.username, user.email, user.password, user.is_admin)
#     )

def create_customer(user_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES ('{user_id}', '{username}', '{email}', '{password}', NULL, 0);"""
    cur.execute(query)
    cur.execute(f"""INSERT INTO Customers (user_id) VALUES ('{user_id}')""")
    con.commit()
    con.close()


def _exists(table, **kwargs):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Can't check if exists if there's no attribute
    assert not kwargs, "Must check at least 1 attribute"

    selection = []

    for attribute, value in kwargs:
        selection.append(f"""{attribute} = {repr(value)}""")

    selection = " OR ".join(selection)

    query = f"""SELECT * FROM {table} WHERE {selection};"""

    result = cur.execute(query).fetchone()

    return bool(result)


def email_exists(email):
    return _exists("Users", email=email)

def username_exists(username):
    return _exists("Users", username=username)

def admin_exists():
    return username_exists("admin")



def user_auth(username, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE username = '{username}' and password = '{password}';"""
    user_data = cur.execute(query).fetchone()
    con.close()
    return user_data


def get_user(user_id):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE user_id = '{user_id}';"""
    user_data = cur.execute(query).fetchone()
    con.close()
    return user_data


def create_admin(admin_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES('{admin_id}', '{username}', '{email}', '{password}', NULL, 1);"""
    cur.execute(query)
    con.commit()
    con.close()
