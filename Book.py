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
    cover_img: str

    def __post_init__(self):
        self.cover_img = BOOK_IMG_UPLOAD_FOLDER + self.cover_img
