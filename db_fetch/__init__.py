from contextlib import closing
import sqlite3

DATABASE = r"database.db"


def execute_db(query: str, parameters) -> list:
    """ Execute sql query with parameters """

    # Ensure that query statement ends properly
    assert query.strip().endswith(";"), 'Must end SQL query with ";"'

    # Use with statement to ensure proper closing of file
    with closing(sqlite3.connect(DATABASE)) as connection:
        with connection:

            # Cursor for executing queries
            cursor = connection.cursor()

            # Execute parameterised queries
            data = cursor.execute(query, parameters).fetchall()

            # Return fetched data (if any)
            return data

    # Code should never reach here, raise error just in case
    raise RuntimeError("unknown critical error")


def retrieve_db(table: str, *columns: str, or_and: int=0, limit: int=0, offset: int=0, **attributes) -> list[tuple]:
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
    return execute_db(query, tuple(attributes.values()))


def insert_row(table: str, values) -> None:
    """ Inserts new row with values into table """

    # Values shouldn't be empty
    assert values, "I'm guessing that you are inserting values, right?"

    # Generate question marks used for parameterised query
    question_marks = ",".join("?"*len(values))

    # Format query statement
    query = f"""INSERT INTO {table} VALUES({question_marks});"""

    # Execute parameterised SQL query 
    execute_db(query, values)


def delete_rows(table: str, or_and: int=0, **attributes) -> None:
    """ Deletes rows from database """

    # At least 1 attribute needs to be specified
    assert attributes, "Must specify at least one attribute"

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


def create_customer(user_id, username, email, password):
    """ Creates a new customer account in the database """

    # Insert user data into Users table
    query = f"""INSERT INTO Users VALUES (?, ?, ?, ?, NULL, 0);"""
    execute_db(query, (user_id, username, email, password))

    # Insert customer details into Customers table
    query = f"""INSERT INTO Customers (user_id) VALUES (?);"""
    execute_db(query, (user_id,))


def _exists(table, **kwargs):
    """ Checks if attribute value pair exists in the table """

    # Can't check if exists if there's no attribute
    assert kwargs, "Must check at least one attribute"

    # Return True non-empty tuple is return
    return bool(retrieve_db(table, **kwargs))


def email_exists(email):
    return _exists("Users", email=email)


def username_exists(username):
    return _exists("Users", username=username)


def admin_exists():
    return username_exists("admin")


def user_auth(username, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE (username = ? OR email = ?) AND password = ?;"""
    creds = (username, username, password)  # 2 usernames looks odd, but it's needed for username and email lol
    user_data = cur.execute(query, creds).fetchone()
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


def retrieve_customer_details(user_id: str):
    """ Returns details of customer """

    # Retrieve customer details from database
    customer_details = retrieve_db(
        "Customers",
        "name", "credit_card_no", "address", "phone_no",
        user_id=user_id
    )

    # Returns a tuple if found else None
    if customer_details:
        return customer_details[0]


def create_admin(admin_id, username, email, password):
    insert_row("Users", (admin_id, username, email, password, None, 1))


def update_customer_account(details1, details2):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Customers (name, phone_no) VALUES (?,?);"""
    query2 = f"""INSERT INTO Users (profile_pic) VALUES (?);"""
    cur.execute(query, details1)
    cur.execute(query2, details2)
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

# Nothing here yet?
