from contextlib import closing
import sqlite3

DATABASE = r"database.db"


def retrieve_db(table, *columns, or_and=0, **attributes):
    """ Retrieve rows from table """

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    if columns:  # If columns were specified

        # Construct projection statement
        projection = ", ".join(columns)

    else:  # If no columns were specified

        # Project all columns
        projection = "*"

    if attributes:  # If attributes were specified

        # Selection statements
        selection = []

        # Loop through attribute and value pairs and format there
        for attribute, value in attributes.items():
            selection.append(f"{attribute} = {repr(value)}")

        # Join statements with "OR"/"AND" if more than one
        selection = " WHERE " + (" OR ", " AND ")[or_and].join(selection)

    else:  # If no attributes were specified

        # No selection options
        selection = ""

    # Create query
    query = f"""SELECT {projection} FROM {table}{selection};"""

    # Fetch and return results of the query
    return cur.execute(query).fetchall()


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
    """ Checks if attribute value pair exists in the table """

    # Can't check if exists if there's no attribute
    assert kwargs, "Must check at least 1 attribute"

    # Return True non-empty tuple is return, else False 
    return bool(retrieve_db(table, **kwargs))


def email_exists(email):
    return _exists("Users", email=email)


def username_exists(username):
    return _exists("Users", username=username)


def admin_exists():
    return username_exists("admin")


def user_auth(username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE username = '{username}' AND password = '{password}';"""
    user_data = cur.execute(query).fetchone()
    con.close()
    return user_data


def retrieve_user(user_id):
    """ Returns user_data using user_id """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE user_id = '{user_id}';"""
    user_data = cur.execute(query).fetchone()
    con.close()

    # Returns a tuple if found else None
    return user_data


def create_admin(admin_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES('{admin_id}', '{username}', '{email}', '{password}', NULL, 1);"""
    cur.execute(query)
    con.commit()
    con.close()
