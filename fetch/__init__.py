from contextlib import closing
import sqlite3

DATABASE = r"database.db"

def fetch_db(sql:str, parameters):
    with closing(sqlite3.connect(DATABASE)) as con:
        with con:
            cur = con.cursor()
            data = cur.execute(sql, parameters).fetchall()
            return data
