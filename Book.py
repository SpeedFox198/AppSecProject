from dataclasses import dataclass

BOOK_IMG_UPLOAD_FOLDER = r"/static/img/books/"


@dataclass
class Book:
    """ Defines a Book object """
    book_id: str
    language: str
    genre: str
    title: str
    stock: int
    price: float
    author: str
    description: str
    _cover_img: str

    @property
    def cover_img(self):
        return BOOK_IMG_UPLOAD_FOLDER + self._cover_img
