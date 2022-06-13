class Book:

    """
    Create book object

    Attributes:
        book_id (str): unique ID identifier of book
        language (str): book language
        category (str): book category
        title (str): book title
        author (str): book author
        price (int): book price
        qty (int): book quantity
        desc (str): book description
        img (str): path of book cover image
    """

    def __init__(self, book_id, language, category, title, qty, price, author, desc, img):
        self.book_id = book_id
        self.language = language
        self.category = category
        self.title = title
        self.author = author
        self.price = price
        self.qty = qty
        self.desc = desc
        self.img = img

    # Mutator methods

    def set_book_id(self, book_id):
        self.book_id = book_id

    def set_language(self, language):
        self.language = language

    def set_category(self, category):
        self.category = category

    def set_title(self, title):
        self.title = title

    def set_author(self, author):
        self.author = author

    def set_price(self, price):
        self.price = price

    def set_qty(self, qty):
        self.qty = qty

    def set_desc(self, desc):
        self.desc = desc

    def set_img(self, img):
        self.img = img

    # Accessor methods
    def get_book_id(self):
        return self.book_id

    def get_language(self):
        return self.language

    def get_category(self):
        return self.category

    def get_title(self):
        return self.title

    def get_author(self):
        return self.author

    def get_price(self):
        return self.price

    def get_qty(self):
        return self.qty

    def get_desc(self):
        return self.desc

    def get_img(self):
        return self.img
