import sqlite3

con = sqlite3.connect("database.db")

# Very scary code, resets your database
# with open("schema.sql") as f:
#     con.executescript(f.read())

# cur = con.cursor()

# cur.execute("""CREATE TABLE OTP (
#     user_id TEXT NOT NULL,
#     otp TEXT NOT NULL,
#     FOREIGN KEY (user_id) REFERENCES Users(user_id)
# );""")
# con.commit()

# x = cur.execute("SELECT * FROM Customers;").fetchall()
# for i in x:
#     print(i)
# q = "DELETE FROM Customers WHERE user_id = 'one' or user_id = 'two';"
# cur.execute(q)
# x = cur.execute("SELECT * FROM Customers;").fetchall()
# for i in x:
#     print(i)

con.commit()
con.close()
