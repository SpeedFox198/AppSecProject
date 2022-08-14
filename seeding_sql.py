import sqlite3

con = sqlite3.connect("database.db")

# Seed the database
with open("seed.sql") as f:
    con.executescript(f.read())

con.commit()
con.close()

print("\033[0;31mScript executed!\033[0m")
