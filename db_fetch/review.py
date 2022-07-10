"""
Review Functions
----------------

Contains functions that interacts with customer reviews in database
"""
from .general import *


# TODO: not done yet @SpeedFox198
# TODO: @Royston - add limiting for ur API rate limiting
def retrieve_reviews(book_id: str) -> list[tuple]:
    """ Retrieve all customer reviews for book """
    return retrieve_db(
        "Reviews NATURAL JOIN Users",
        ("username", "profile_pic", "stars", r"STRFTIME('%d/%m/%Y %H:%M', DATETIME(time, 'localtime'))", "content"),
        limit=0, offset=0,  # TODO currently at default values, to be changed when creating API
        book_id=book_id
    )


def retrieve_reviews_ratings(book_id: str) -> Union[float, None]:
    """ Retrieve average star ratings of book """
    data = retrieve_db("Reviews", ("AVG(stars)",), fetchone=True, book_id=book_id)
    if data:
        return data[0]


def add_review(book_id: str, user_id: str, stars: int, content: str) -> None:
    """ Adds a new customer review into database """
    insert_row(
        "Reviews",
        [book_id, user_id, stars, content],
        ["book_id", "user_id", "stars", "content"]
    )
