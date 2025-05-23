import sqlite3
from tabulate import tabulate

def remove_user_city(user_id: int):
    cur.execute("UPDATE users SET city = NULL, country = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    
    conn.close()

conn = sqlite3.connect("users.db")
cur = conn.cursor()

def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            city TEXT,
            country TEXT
        )
    """)
    conn.commit()
    conn.close()


# db.py
def set_user_city(user_id: int, city: str, country: str):
    # ??????? ?????? ??? ???????? ?????? ? ??????
    cur.execute("INSERT OR REPLACE INTO users (user_id, city, country) VALUES (?, ?, ?)", (user_id, city, country))
    conn.commit()
    print(f"????? ??? ???????????? {user_id} ?????????? ??? {city}, {country}")

def get_user_city(user_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT city, country FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1]  # ?????????? ? ?????, ? ??????
    return None, None


def get_all_users():
    cur.execute("SELECT user_id, city, country FROM users")
    users = cur.fetchall()
    # ?????????? tabulate ??? ?????? ???????? ???????
    print(tabulate(users, headers=["User ID", "City", "Country"], tablefmt="pretty"))
    return users
