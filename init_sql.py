import sqlite3

con = sqlite3.connect("database.db")

# Very scary code, resets your database
# with open("schema.sql") as f:
#     con.executescript(f.read())

cur = con.cursor()
cur.execute("""CREATE TABLE Timeout (
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    timeout_year INTEGER NOT NULL,
    timeout_month INTEGER NOT NULL,
    timeout_day INTEGER NOT NULL,
    timeout_hour INTEGER NOT NULL,
    timeout_minute INTEGER NOT NULL,
    timeout_second INTEGER NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username)
);
""")
con.commit()

# x = cur.execute("SELECT * FROM Customers;").fetchall()
# for i in x:
#     print(i)
# q = "DELETE FROM Customers WHERE user_id = 'one' or user_id = 'two';"
# cur.execute(q)
# x = cur.execute("SELECT * FROM Customers;").fetchall()
# for i in x:
#     print(i)

# Generate data if we need to fill in
# INSERT into Books VALUES ('19a4cc17-117a-4a20-8ad6-cc3c243e68a7', 'English', 'Classic', "Jabriel's Python Manifesto", 30, 25, 'Jabriel Seah', 'This 3rd edition features decorators, TimSorts, awesome stacks and queues, and async/await. Definitely, one of the python books of all time. Ultra Poggers.', '19a4cc17-117a-4a20-8ad6-cc3c243e68a7_python2.jpg');
# INSERT INTO Users VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6", "TestUser1", "test@user.mail", "Test1234", "54dd57bf-8b8e-5cc1-af95-14478ca84b21_padoru.png", "customer");
# INSERT INTO Customers (user_id) VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6");

con.commit()
con.close()
