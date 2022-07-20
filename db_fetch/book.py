"""
Book Functions
--------------

Contains functions that interact with book information
"""
from .general import *

""" User-triggered Functions """


def retrieve_books_by_language(book_language):
    return retrieve_db("Books", language=book_language)


def retrieve_inventory():
    return retrieve_db("Books")


def retrieve_book(id_of_book: str) -> Union[tuple, None]:
    """ Retrieves details of the book """
    return retrieve_db("Books", book_id=id_of_book, fetchone=True)


def number_of_books():
    return retrieve_db("Books", columns=["COUNT(*)"])[0][0]


""" Admin-triggered Functions """


def book_add(details: tuple):
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = "INSERT INTO Books VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);"
    # cur.execute(query, details)
    # con.commit()
    # con.close()
    insert_row("Books", details)


def book_update(details: tuple, book_id: str):
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = "UPDATE Books SET language = ?, genre = ?, title = ?, stock = ?, price = ?, author = ?, description = ?, cover_img = ? WHERE book_id = ?;"
    # cur.execute(query, details)
    # con.commit()
    # con.close()
    update_rows("Books", ["language", "genre", "title", "stock", "price", "author", "description", "cover_img"], values=details, book_id=book_id)


def delete_book(id_of_book: str):
    # con = sqlite3.connect(DATABASE)
    # cur = con.cursor()
    # query = "DELETE FROM Books WHERE book_id = ?;"
    # cur.execute(query, (id_of_book,))
    # con.commit()
    # con.close()
    delete_rows("Books", book_id=id_of_book)
