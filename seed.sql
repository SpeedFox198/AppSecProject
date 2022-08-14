-- Books
INSERT INTO Books
VALUES (
    "19a4cc17-117a-4a20-8ad6-cc3c243e68a7",
    "English", "Classic", "Jabriel's Python Manifesto",
    30, 25,
    "Jabriel Seah",
    "This 3rd edition features decorators, TimSorts, awesome stacks and queues, and async/await. Definitely, one of the python books of all time. Ultra Poggers.",
    "19a4cc17-117a-4a20-8ad6-cc3c243e68a7_python2.jpg"
);

-- Admin
INSERT INTO Users
VALUES (
    "bace0701-15e3-5144-97c5-47487d543032",
    "admin",
    "admin@vsecurebookstore.com",
    "PASS{uNh@5h3d}",
    NULL,
    "admin"
);

-- Customers
INSERT INTO Users
VALUES (
    "5a851b9e-48dc-5c81-9039-720c9f0b41a6",
    "TestUser1",
    "test@user.mail",
    "Test1234",
    "54dd57bf-8b8e-5cc1-af95-14478ca84b21_padoru.png",
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6");
INSERT INTO Users
VALUES (
    "5764d848-a0dc-5857-b4fd-31102dc764dc",
    "MikuBlyat",
    "roystonloo54@gmail.com",
    "Pa$$w0rd",
    null,
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5764d848-a0dc-5857-b4fd-31102dc764dc");

-- Reviews
INSERT INTO Reviews (book_id, user_id, stars, content)
VALUES (
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5a851b9e-48dc-5c81-9039-720c9f0b41a6',
    2, 'This book did not make me prepare for recursion during my Data Structures test.');
