"""
Order Functions
---------------

Contains functions that interact with orders table
"""
from .general import *


def create_order_details(order_id, user_id, shipping_option, order_status):
    """ Create order details """
    insert_row("OrderDetails", [order_id, user_id, shipping_option, order_status], ['order_id', 'user_id', 'shipping_option', 'order_pending'])

def create_order_items(order_id, book_id, quantity):
    insert_row("OrderItems", [order_id, book_id, quantity])


def get_order_details(user_id):
    """ Returns order details using order_id"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""SELECT * FROM OrderDetails WHERE user_id = '{user_id}';"""
    # order_data = cur.execute(query).fetchone()
    # con.close()
    return retrieve_db("OrderDetails", user_id=user_id)


def get_order_items(order_id):
    """ Returns book's order items using book_id"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""SELECT quantity FROM OrderItems WHERE book_id = '{book_id}';"""
    # order_items = cur.execute(query).fetchone()
    # con.close()
    return retrieve_db("OrderItems", ["book_id", "quantity"], order_id=order_id)


def get_all_orders():
    return retrieve_db("OrderDetails")


def number_of_orders():
    return retrieve_db("OrderDetails", columns=["COUNT(*)"])[0][0]
