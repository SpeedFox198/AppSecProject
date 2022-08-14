import sqlite3

con = sqlite3.connect("database.db")

# Very scary code, resets your database
# with open("schema.sql") as f:
#     con.executescript(f.read())

cur = con.cursor()
cur.execute("""CREATE TABLE OTP (
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
""")

# Generate data if we need to fill in
# q1 = """ INSERT into Books VALUES ('19a4cc17-117a-4a20-8ad6-cc3c243e68a7', 'English', 'Classic', "Jabriel's Python Manifesto", 30, 25, 'Jabriel Seah', 'This 3rd edition features decorators, TimSorts, awesome stacks and queues, and async/await. Definitely, one of the python books of all time. Ultra Poggers.', '19a4cc17-117a-4a20-8ad6-cc3c243e68a7_python2.jpg'); """
# q2 = """ INSERT INTO Users VALUES ("bace0701-15e3-5144-97c5-47487d543032", "admin", "admin@vsecurebookstore.com", "PASS{uNh@5h3d}", NULL, "admin"); """
# q3 = """ INSERT INTO Users VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6", "TestUser1", "test@user.mail", "Test1234", "54dd57bf-8b8e-5cc1-af95-14478ca84b21_padoru.png", "customer"); """
# q4 = """ INSERT INTO Customers (user_id) VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6"); """
# q5 = """ INSERT INTO Reviews (book_id, user_id, stars, content) VALUES ('19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5a851b9e-48dc-5c81-9039-720c9f0b41a6', 2, 'This book did not make me prepare for recursion during my Data Structures test.'); """
# cur.execute(q1)
# cur.execute(q2)
# cur.execute(q3)
# cur.execute(q4)
# cur.execute(q5)

con.commit()
con.close()

print("\033[0;31mScript executed!\033[0m")
