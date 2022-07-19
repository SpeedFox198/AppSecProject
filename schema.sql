-- DROP TABLE IF EXISTS Users;
-- DROP TABLE IF EXISTS OTP;
-- DROP TABLE IF EXISTS Customers;
-- DROP TABLE IF EXISTS Books;
-- DROP TABLE IF EXISTS OrderDetails;
-- DROP TABLE IF EXISTS OrderItems;
-- DROP TABLE IF EXISTS CartItems;
-- DROP TABLE IF EXISTS Reviews;

CREATE TABLE Users (
    user_id TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    profile_pic TEXT,
    is_admin INTEGER NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE twoFA (
    user_id TEXT NOT NULL,
    twoFA_secret_token TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE OTP (
    user_id TEXT NOT NULL,
    otp TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Customers (
    user_id TEXT NOT NULL,
    name TEXT,
    credit_card_no TEXT,
    address TEXT,
    phone_no INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Books (
    book_id TEXT NOT NULL,
    language TEXT NOT NULL,
    genre TEXT NOT NULL,
    title TEXT NOT NULL,
    stock INTEGER NOT NULL,
    price INTEGER NOT NULL,
    author TEXT NOT NULL,
    description TEXT NOT NULL,
    cover_img TEXT NOT NULL,
    PRIMARY KEY (book_id)
);

CREATE TABLE OrderDetails (
    order_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipping_option TEXT NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE OrderItems (
    order_id TEXT NOT NULL,
    book_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES OrderDetails(order_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE CartItems (
    user_id TEXT NOT NULL,
    book_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
);

CREATE TABLE Reviews (
    book_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    stars INTEGER NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
