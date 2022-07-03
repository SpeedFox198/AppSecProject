"""
Review Functions
----------------

Contains functions that interacts with customer reviews in database
"""
from .general import *


# TODO: not done yet @SpeedFox198
def retrieve_reviews(book_id: str) -> list[tuple]:
    """ Retrieve all customer reviews for book """
    return retrieve_db("Reviews R INNER JOIN Customers C", [])
