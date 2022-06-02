from contextlib import closing
import sqlite3

DATABASE = r"database.db"


def fetch_db(sql: str, parameters):
    with closing(sqlite3.connect(DATABASE)) as con:
        with con:
            cur = con.cursor()
            data = cur.execute(sql, parameters).fetchall()
            return data


# def create_user(user):
#     fetch_db(
#         """INSERT INTO Users VALUES (?, ?, ?, ?, NULL, ?)""",
#         (user.id, user.username, user.email, user.password, user.is_admin)
#     )

def create_user(user):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES ({user.id}, {user.username}, {user.email}, {user.password}, NULL, {user.is_admin});"""
    cur.execute(query)
    con.commit()
    con.close()


def get_user(form):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE username = {form.username.data} and password = {form.username.data};"""
    user_data = cur.execute(query).fetchone()
    con.close()
    return user_data


def admin_exists():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""SELECT * FROM Users WHERE username = 'admin';"""
    exist = cur.execute(query).fetchone()
    con.close()
    return bool(exist)


def create_admin(admin_id, username, email, password):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = f"""INSERT INTO Users VALUES({admin_id}, {username}, {email}, {password}, NULL, 1);"""
    cur.execute(query)
    con.commit()
    con.close()
