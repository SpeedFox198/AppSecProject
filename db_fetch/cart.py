"""
Cart Functions
--------------

Contains functions that interacts with customer cart items
"""
from .general import *


def add_to_shopping_cart(user_id: str, book_id: str, quantity: int) -> None:
    """ Add new cart item into database """
    insert_row("CartItems", (user_id, book_id, quantity))


def update_shopping_cart(user_id: str, book_id: str, quantity: int) -> None:
    """ Update quantity of shopping cart """
    update_rows("CartItems", ["quantity"], [quantity], or_and=1, user_id=user_id, book_id=book_id)


def get_shopping_cart(user_id):
    """ Returns user's shopping cart info using user_id"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""SELECT book_id, quantity FROM CartItems WHERE user_id = '{user_id}';"""
    # cart_data = cur.execute(query).fetchall()
    # con.close()

    # return cart_data
    return retrieve_db("CartItems", ["book_id", "quantity"], user_id=user_id)


def get_cart_item(user_id: str, book_id: str) -> Union[tuple, None]:
    """ Returns the cart item storing book_id of user if found """
    return retrieve_db("CartItems", or_and=1, user_id=user_id, book_id=book_id, fetchone=True)


def delete_shopping_cart_item(user_id, book_id):
    """ Deletes user's shopping cart"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""DELETE FROM CartItems WHERE user_id = '{user_id}';"""
    # cur.execute(query)
    # con.close()
    delete_rows("CartItems", user_id=user_id, or_and=1, book_id=book_id)
