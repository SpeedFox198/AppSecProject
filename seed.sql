DELETE FROM Users;
DELETE FROM OTP;
DELETE FROM Customers;
DELETE FROM Books;
DELETE FROM OrderDetails;
DELETE FROM OrderItems;
DELETE FROM CartItems;
DELETE FROM Reviews;
DELETE FROM TwoFA;
DELETE FROM Timeout;
DELETE FROM FailedAttempts;

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
INSERT INTO Books
VALUES (
    "e97850e7-a345-4d5c-8863-12654b08b64c",
    "English", "Classic", "To Kill a Mockingbird",
    100, 20,
    "Harper Lee",
    'The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it. "To Kill A Mockingbird" became both an instant bestseller and a critical success when it was first published in 1960. It went on to win the Pulitzer Prize in 1961 and was later made into an Academy Award-winning film, also a classic.',
    "e97850e7-a345-4d5c-8863-12654b08b64c.jpg"
);


-- Admin
INSERT INTO Users
VALUES (
    "bace0701-15e3-5144-97c5-47487d543032",
    "admin",
    "gAAAAABi-IfZSBv2-ZxH-fyE4y3dQhfmrwqIBL2R-07iRTzt7W23M5nd_UGrFPlbhQ1IvPhNNtReJFnoDZzvDGJDgJXKrld-R7WuaqZujGrOzrfw5wq-V8M=",
    "$argon2id$v=19$m=65536,t=3,p=4$acynvM4ydSviKYLByUPFmw$2YPqGEVRIguIrwIceezc1DV/2afbBggpZmwZAq/lb9g",
    NULL,
    "admin"
);


-- Customers
INSERT INTO Users
VALUES (
    "5a851b9e-48dc-5c81-9039-720c9f0b41a6",
    "TestUser1",
    "gAAAAABi-Ip__un5XV9_BwDNNwerve-owD904RUtL9aZgoUksAOOTNB8GcNZIaWeN6PPQxznNtXlVYzMd9BPbgygFCH81737UQ==",
    "$argon2id$v=19$m=65536,t=3,p=4$qVMQ9JdyLcF8BNwG/Uen4g$M5pqQTXy69SaIqzMLYM/OR6jj3qRt4MNQkK2Sbabm50",
    "54dd57bf-8b8e-5cc1-af95-14478ca84b21_padoru.png",
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6");
INSERT INTO Users
VALUES (
    "5764d848-a0dc-5857-b4fd-31102dc764dc",
    "MikuBlyat",
    "gAAAAABi-Ip_lxqFpTJHYFLgnFJFaLVCsz8LU2HLT20oK2qDex9gZ5kDvTS_mAVcKUKKwEwHwzVQHcDGYbrX2D87STZQoxuqcXTPhF1jaaoiahIrIZGzVHo=",
    "$argon2id$v=19$m=65536,t=3,p=4$e/V/+PieUJgKK6dF9Oy6Dw$MkwfAvYRRPe8TtbJzspZbLgcBxlbjPX7qerwzQDrq+I",
    NULL,
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5764d848-a0dc-5857-b4fd-31102dc764dc");
INSERT INTO OTP VALUES (
    "5764d848-a0dc-5857-b4fd-31102dc764dc",
    191605, 2022, 7, 26, 9, 54, 57
);


-- Reviews
INSERT INTO Reviews (book_id, user_id, stars, content)
VALUES (
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5a851b9e-48dc-5c81-9039-720c9f0b41a6',
    2, 'This book did not make me prepare for recursion during my Data Structures test.'
);
INSERT INTO Reviews (book_id, user_id, stars, content)
VALUES (
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5764d848-a0dc-5857-b4fd-31102dc764dc',
    5, 'Learn a lot and got a job at Google with this book!'
);
