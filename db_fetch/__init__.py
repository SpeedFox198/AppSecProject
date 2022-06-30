from contextlib import closing
from typing import Union
import sqlite3

DATABASE = r"database.db"


""" General Operations Functions """


def execute_db(query: str, parameters, fetchone=False) -> Union[list[tuple], tuple, None]:
    """ Execute sql query with parameters """

    # Ensure that query statement ends properly
    assert query.strip().endswith(";"), 'Must end SQL query with ";"'

    # Use with statement to ensure proper closing of file
    with closing(sqlite3.connect(DATABASE)) as connection:
        with connection:

            # Cursor for executing queries
            cursor = connection.cursor()

            # Execute parameterised queries
            retrieved = cursor.execute(query, parameters)

            if fetchone:
                data = retrieved.fetchone()
            else:
                data = retrieved.fetchall()

            # Return fetched data (if any)
            return data

    # Code should never reach here, raise error just in case
    raise RuntimeError("Unknown critical error!")


def retrieve_db(table: str, columns: list=None, or_and: int=0, limit: int=0, offset: int=0, fetchone=False, **attributes) -> Union[list[tuple], tuple, None]:
    """
    Retrieve rows from table

    Args:
        table (str): Table to be retrieved.
        columns (:obj:`list`, optional): Columns to be projected.
        or_and (:obj:`int`, optional): 0 for OR, 1 for AND.
        limit (:obj:`int`, optional): Limits the number of rows retrieved
        offset (:obj:`int`, optional): Offset of index to start retrieving from
        fetchone (:obj:`bool`, optional): Fetches one row only if set to True
        **attributes: Attributes to be selected.

    Returns:
        list[tuple] | tuple | None: Data retrieved
    """

    # Default values of statements
    projection = "*"   # Project all columns
    selection = ""     # No selection options
    limit_offset = ""  # No limit

    if columns:  # If columns were specified

        # Construct projection statement
        projection = ",".join(columns)

    if attributes:  # If attributes were specified

        # Selection statements
        selection = []

        # Loop through attributes and add parameterised statements
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
    query = f"""SELECT {projection} FROM {table} {selection} {limit_offset};"""

    # Fetch and return results of the query
    return execute_db(query, tuple(attributes.values()), fetchone)


def insert_row(table: str, values: list, columns: list=None) -> None:
    """ Inserts new row with values into, columns of table """

    # Values shouldn't be empty
    if not values:
        raise ValueError("Must specify at least one value to be inserted")

    # Generate question marks used for parameterised query
    question_marks = ",".join("?"*len(values))

    # Format column names (default nothing)
    column_names = ",".join(columns)
    if column_names:
        column_names = f"({column_names})"

    # Format query statement
    query = f"""INSERT INTO {table} {column_names} VALUES ({question_marks});"""

    # Execute parameterised SQL query 
    execute_db(query, values)


def delete_rows(table: str, or_and: int=0, **attributes) -> None:
    """ Deletes rows from table """

    # At least one attribute needs to be specified
    if not attributes:
        raise TypeError("Must specify at least one attribute")

    # Selection statements
    selection = []

    # Loop through attributes and add parameterised statements
    for attribute in attributes:
        selection.append(f"{attribute} = ?")

    selection = (" OR ", " AND ")[or_and].join(selection)

    # Format query statement
    query = f"""DELETE FROM {table} WHERE {selection};"""

    # Execute parameterised query
    execute_db(query, tuple(attributes.values()))


def update_rows(table: str, columns: list[str], values: list, or_and: int=0, **attributes) -> None:
    """ Updates rows of table """

    # At least one column should be updated
    if not columns:
        raise ValueError("Must specify at least column to be updated")

    # Each column needs a corresponding value
    elif len(columns) != len(values):
        raise ValueError("Columns and values must be of same length")

    # At least one attribute needs to be specified
    elif not attributes:
        raise TypeError("Must specify at least one attribute")

    # Format columns
    temp = []  # Temp 
    for column in columns:
        temp.append(f"{column} = ?")
    columns_str = ",".join(temp)

    # Selection statements
    selection = []
    # Loop through attributes and add parameterised statements
    for attribute in attributes:
        selection.append(f"{attribute} = ?")
    selection = (" OR ", " AND ")[or_and].join(selection)

    query = f"""UPDATE {table} SET {columns_str} WHERE {selection};"""

    params = tuple(values) + tuple(attributes.values())

    execute_db(query, params)


def create_customer(user_id, username, email, password) -> None:
    """ Creates a new customer account in the database """

    # Insert user data into Users table
    insert_row("Users", (user_id, username, email, password, None, 0))

    # Insert customer details into Customers table
    insert_row("Customers", (user_id,), ("user_id",))


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


def retrieve_customer_details(user_id: str) -> Union[tuple, None]:
    """ Returns details of customer """
    return retrieve_db(
        "Customers",
        columns=("name", "credit_card_no", "address", "phone_no"),
        user_id=user_id,
        fetchone=True
    )


def create_admin(admin_id: str, username: str, email: str, password: str) -> None:
    """ Creates an admin account """
    insert_row("Users", (admin_id, username, email, password, None, 1))


def update_customer_account(details1, details2):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """UPDATE Customers SET name = ?, phone_no = ? where user_id = ?;"""
    query2 = """UPDATE Users SET profile_pic = ? where user_id = ?;"""
    cur.execute(query, details1)
    cur.execute(query2, details2)
    con.commit()
    con.close()


def retrieve_books_by_language(book_language):
    return retrieve_db("Books", language=book_language)


""" Customer-triggered Fuctions """


def change_password(user_id: str, password: str) -> None:
    """ Updates user's password to new value """
    update_rows("Users", ("password"), (password,), user_id=user_id)


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
    return retrieve_db("Books", book_id=id_of_book, fetchone=True)


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


def retrieve_these_customers(limit:int, offset: int) -> list[tuple]:
    """ Retrieves and returns a list of max 10 customers starting from offset """
    return retrieve_db("Users NATURAL JOIN Customers", limit=limit, offset=offset, is_admin=0)


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

def add_existing_to_shopping_cart(user_id, book_id, quantity):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""UPDATE CartItems SET quantity = quantity + {quantity} WHERE user_id = '{user_id}' AND book_id = '{book_id}';"""
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
