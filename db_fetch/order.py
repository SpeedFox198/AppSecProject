"""
Order Functions
---------------

Contains functions that interact with orders table
"""
from .general import *


def create_order_details(order_id, user_id, shipping_option, order_pending):
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""INSERT INTO OrderDetails VALUES('{order_id}', '{user_id}', '{shipping_option}', '{order_pending}');"""
    # cur.execute(query)
    # con.commit()
    # con.close()
    insert_row("OrderDetails", [order_id, user_id, shipping_option, order_pending])


def get_order_details(user_id):
    """ Returns order details using order_id"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""SELECT * FROM OrderDetails WHERE user_id = '{user_id}';"""
    # order_data = cur.execute(query).fetchone()
    # con.close()
    return retrieve_db("OrderDetails", user_id=user_id, fetchone=True)


def get_order_items(book_id):
    """ Returns book's order items using book_id"""
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = f"""SELECT quantity FROM OrderItems WHERE book_id = '{book_id}';"""
    # order_items = cur.execute(query).fetchone()
    # con.close()
    return retrieve_db("OrderItems", ["quantity"], book_id=book_id, fetchone=True)
