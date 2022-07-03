"""
Review Functions
----------------

Contains functions that interacts with customer reviews in database
"""
from general import *


# TODO: not done yet @SpeedFox198
def retrieve_reviews(book_id: str) -> list[tuple]:
    """ Retrieve all customer reviews for book """
    return retrieve_db(
        "Reviews NATURAL JOIN Users",
        ["username", "profile_pic", "stars", "time", "content"],
        limit=0, offset=0,  # TODO currently at deafult vcalues, to be changed when creating API
        book_id=book_id
    )
