"""
Review Functions
----------------

Contains functions that interacts with customer reviews in database
"""
from .general import *


# TODO: not done yet @SpeedFox198
def retrieve_reviews(book_id: str) -> list[tuple]:
    """ Retrieve all customer reviews for book """
    return retrieve_db(
        "Reviews NATURAL JOIN Users",
        ["username", "profile_pic", "stars", r"STRFTIME('%d/%m/%Y %H:%M', DATETIME(time, 'localtime'))", "content"],
        limit=0, offset=0,  # TODO currently at deafult vcalues, to be changed when creating API
        book_id=book_id
    )


def add_review(book_id: str, user_id: str, stars: int, content: str) -> None:
    """ Adds a new customer review into database """
    insert_row(
        "Reviews",
        [book_id, user_id, stars, content],
        ["book_id", "user_id", "stars", "content"]
    )

if __name__ == "__main__":
    testUser = "54dd57bf-8b8e-5cc1-af95-14478ca84b21"
    MikuBlyat = "5764d848-a0dc-5857-b4fd-31102dc764dc"
    book = "19a4cc17-117a-4a20-8ad6-cc3c243e68a7"
    add_review(book, MikuBlyat, 0, "Horrible book, I don't recommend this, aa, itsumo no you ni sugiru hibi ni akubi ga deru sanzameku yoru, koe, kyou mo shibuya no machi ni asa ga furu dokoka munashii you na sonna kimochi tsumaranai na demo sore de ii sonna mon sa kore de ii")
