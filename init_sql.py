import sqlite3

con = sqlite3.connect("database.db")

# Very scary code, resets your database
with open("schema.sql") as f:
    con.executescript(f.read())

# cur = con.cursor()

# cur.execute("DELETE FROM Users WHERE 1=1")
# con.commit()

# x = cur.execute("SELECT * FROM Users").fetchall()
# for i in x:
#     print(i)

con.commit()
con.close()
