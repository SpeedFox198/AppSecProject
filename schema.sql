-- DROP TABLE IF EXISTS Users;
-- DROP TABLE IF EXISTS OTP;
-- DROP TABLE IF EXISTS Customers;
-- DROP TABLE IF EXISTS Books;
-- DROP TABLE IF EXISTS OrderDetails;
-- DROP TABLE IF EXISTS OrderItems;
-- DROP TABLE IF EXISTS CartItems;
-- DROP TABLE IF EXISTS Reviews;
-- DROP TABLE IF EXISTS TwoFA;
-- DROP TABLE IF EXISTS Timeout;
-- DROP TABLE IF EXISTS FailedAttempts;
-- DROP TABLE IF EXISTS BackUpCodes;

CREATE TABLE Users (
    user_id TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    profile_pic TEXT,
    role TEXT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE TwoFA (
    user_id TEXT NOT NULL,
    twoFA_secret_token TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE BackUpCodes (
    user_id TEXT NOT NULL,
    backupcode1 TEXT NOT NULL,
    backupcode2 TEXT NOT NULL,
    backupcode3 TEXT NOT NULL,
    backupcode4 TEXT NOT NULL,
    backupcode5 TEXT NOT NULL,
    backupcode6 TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE FailedAttempts (
    user_id TEXT NOT NULL,
    attempts INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Timeout (
    user_id TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    second INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE OTP (
    user_id TEXT NOT NULL,
    otp TEXT NOT NULL,
    otp_year INTEGER NOT NULL,
    otp_month INTEGER NOT NULL,
    otp_day INTEGER NOT NULL,
    otp_hour INTEGER NOT NULL,
    otp_minute INTEGER NOT NULL,
    otp_second INTEGER NOT NULL,
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
    title TEXT NOT NULL COLLATE NOCASE,
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
    order_pending TEXT NOT NULL,
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
