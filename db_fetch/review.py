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
        ("user_id", "username", "profile_pic", "stars", r"STRFTIME('%Y-%m-%d %H:%M', DATETIME(time, 'localtime'))", "content"),
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


def retrieve_selected_review(book_id, user_id):
    """Checks if review exists, mostly used for deletion"""
    return retrieve_db("Reviews", book_id=book_id, or_and=1, user_id=user_id)


def delete_review(book_id, user_id):
    """Delete review based on book_id and the user_id"""
    delete_rows("Reviews", book_id=book_id, or_and=1, user_id=user_id)


def no_of_reviews_from_book(book_id):
    return retrieve_db("Reviews", ["COUNT(*)"], fetchone=True, book_id=book_id)[0]


def no_of_all_reviews():
    return retrieve_db("Reviews", ["COUNT(*)"])[0][0]
