class Book:

    """
    Create book object

    Attributes:
        __book_id (str): unique ID identifier of book
        __language (str): book language
        __category (str): book category
        __title (str): book title
        __author (str): book author
        __price (int): book price
        __qty (int): book quantity
        __desc (str): book description
        __img (str): path of book cover image
    """

    count_id = 0

    def __init__(self, language, category, title, qty, price, author, desc, img):
        Book.count_id += 1
        self.__book_id = Book.count_id
        self.__language = language
        self.__category = category
        self.__title = title
        self.__author = author
        self.__price = price
        self.__qty = qty
        self.__desc = desc
        self.__img = img

    # Mutator methods

    def set_book_id(self, book_id):
        self.__book_id = book_id

    def set_language(self, language):
        self.__language = language

    def set_category(self, category):
        self.__category = category

    def set_title(self, title):
        self.__title = title

    def set_author(self, author):
        self.__author = author

    def set_price(self, price):
        self.__price = price

    def set_qty(self, qty):
        self.__qty = qty

    def set_desc(self, desc):
        self.__desc = desc

    def set_img(self, img):
        self.__img = img

    # Accessor methods
    def get_book_id(self):
        return self.__book_id

    def get_language(self):
        return self.__language

    def get_category(self):
        return self.__category

    def get_title(self):
        return self.__title

    def get_author(self):
        return self.__author

    def get_price(self):
        return self.__price

    def get_qty(self):
        return self.__qty

    def get_desc(self):
        return self.__desc

    def get_img(self):
        return self.__img
