from contextlib import closing
import sqlite3

DATABASE = r"database.db"
MAX_ALLOWED_ATTEMPTS = 5


def execute_db(query: str, parameters):
    """ Execute sql query with parameters """
    with closing(sqlite3.connect(DATABASE)) as con:
        with con:
            cur = con.cursor()
            data = cur.execute(query, parameters).fetchall()
            return data


def retrieve_db(table: str, *columns: str, or_and: int=0, limit: int=0, offset: int=0, **attributes) -> list:
    """
    Retrieve rows from table

    Args:
        table (str): Table to be retrieved.
        *columns: Columns to be projected.
        or_and(:obj:`int`, optional): 0 for OR, 1 for AND.
        **attributes: Attributes to be selected.

    Returns:
        list: A list of retrieved rows
    """

    # Connect to database
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Default values of statements
    projection = "*"   # Project all columns
    selection = ""     # No selection options
    limit_offset = ""  # No limit

    if columns:  # If columns were specified

        # Construct projection statement
        projection = ", ".join(columns)

    if attributes:  # If attributes were specified

        # Selection statements
        selection = []

        # Loop through attribute and value pairs and format there
        for attribute in attributes:
            selection.append(f"{attribute} = ?")

        # Join statements with "OR"/"AND" if more than one
        selection = " WHERE " + (" OR ", " AND ")[or_and].join(selection)

    if limit:  # If limits were specified

        # Limits and offsets should be positive
        assert limit >= 0, "Limit should be a int more than 0"
        assert offset >= 0, "Offset should be a int more than 0"

        limit_offset = f" LIMIT {int(limit)} OFFSET {int(offset)}"

    # Create query
    query = f"""SELECT {projection} FROM {table}{selection}{limit_offset};"""

    # Fetch and return results of the query
    return cur.execute(query, tuple(attributes.values())).fetchall()


def delete_rows(table: str, or_and: int=0, **attributes) -> None:
    """ Deletes rows from database """

    # Connect to database
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Selection statements
    selection = []

    # Loop through attribute and value pairs and format there
    for attribute in attributes:
        selection.append(f"{attribute} = ?")

    selection = (" OR ", " AND ")[or_and].join(selection)

    query = f"""DELETE FROM {table} WHERE """

    cur.execute(query, tuple(attributes.values()))


def create_customer(user_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES ('{user_id}', '{username}', '{email}', '{password}', NULL, 0, );"""
    cur.execute(query)
    cur.execute(f"""INSERT INTO Customers (user_id) VALUES ('{user_id}')""")
    con.commit()
    con.close()


def _exists(table, **kwargs):
    """ Checks if attribute value pair exists in the table """

    # Can't check if exists if there's no attribute
    assert kwargs, "Must check at least 1 attribute"

    # Return True non-empty tuple is return
    return bool(retrieve_db(table, **kwargs))


def email_exists(email):
    return _exists("Users", email=email)


def username_exists(username):
    return _exists("Users", username=username)


def retrieve_user_attempts(credentials):
    results = retrieve_db("Users", "attempts", email=credentials, username=credentials)
    if results:
        return results[0][0]
    else:
        return None


def admin_exists():
    return username_exists("admin")


def user_auth(username, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE (username = '{username}' OR email = '{username}') AND password = '{password}';"""
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


def retrieve_customer_details(user_id):
    """ Returns details of customer """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Customers WHERE user_id = '{user_id}';"""
    customer_details = cur.execute(query).fetchone()
    con.close()

    # Returns a tuple if found else None
    return customer_details


def create_admin(admin_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES('{admin_id}', '{username}', '{email}', '{password}', NULL, 1, {MAX_ALLOWED_ATTEMPTS});"""
    cur.execute(query)
    con.commit()
    con.close()


""" Admin Functions """


def retrieve_inventory():
    return retrieve_db("Books")


def book_add(details: tuple):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = "INSERT INTO Books VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"
    cur.execute(query, details)
    con.commit()
    con.close()


def retrieve_book(id_of_book):
    return retrieve_db("Books", book_id=id_of_book)


def book_update(details: tuple):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = "UPDATE Books SET language = ?, genre = ?, title = ?, stock = ?, price = ?, author = ?, description = ?, cover_img = ? WHERE book_id = ?;"
    cur.execute(query, details)
    con.commit()
    con.close()


def delete_book(id_of_book: str):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = "DELETE FROM Books WHERE book_id = ?;"
    cur.execute(query, (id_of_book,))
    con.commit()
    con.close()


def retrieve_these_customers(limit:int, offset: int):
    """ Retrieves and returns a list of max 10 customers starting from offset """
    return retrieve_db("Users NATURAL JOIN Customers", limit=limit, offset=offset, is_admin=0)


def number_of_customers() -> int:
    """ Returns count of number of customers """
    return retrieve_db("Customers", "COUNT(*)")[0][0]


def delete_customer(user_id: str):
    """ Deletes and returns customer from database """
    customer_data = retrieve_db("Customers", user_id=user_id)
    if customer_data:
        delete_rows("Users", user_id=user_id)
        delete_rows("Customers", user_id=user_id)
        return customer_data[0]


""" Start of Order functions"""


def create_order_details(order_id, user_id, shipping_option):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO OrderDetails VALUES('{order_id}', '{user_id}', '{shipping_option}');"""
    cur.execute(query)
    con.commit()
    con.close()


def get_order_details(user_id):
    """ Returns order details using order_id"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM OrderDetails WHERE user_id = '{user_id}';"""
    order_data = cur.execute(query).fetchone()
    con.close()

    return order_data


def get_order_items(book_id):
    """ Returns book's order items using book_id"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT quantity FROM OrderItems WHERE book_id = '{book_id}';"""
    order_items = cur.execute(query).fetchone()
    con.close()

    return order_items


""" End of Order functions"""

""" Start of Shopping Cart functions """


def add_to_shopping_cart(user_id, book_id, quantity):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO CartItems VALUES('{user_id}', '{book_id}', '{quantity}');"""
    cur.execute(query)
    con.commit()
    con.close()


def get_shopping_cart(user_id):
    """ Returns user's shopping cart info using user_id"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT book_id, quantity FROM CartItems WHERE user_id = '{user_id}';"""
    cart_data = cur.execute(query).fetchone()
    con.close()

    return cart_data


""" End of Shopping Cart functions """

""" Royston :D """


def decrease_login_attempts(credentials, attempts):
    """ Decrease user's login attempts and return attempts left """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""UPDATE Users SET attempts = {attempts - 1} WHERE user_id = '{credentials}' OR email = '{credentials}';"""
    cur.execute(query)
    con.commit()
    con.close()
