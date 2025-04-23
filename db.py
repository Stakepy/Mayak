import sqlite3
from tabulate import tabulate

conn = sqlite3.connect("users.db")
cur = conn.cursor()

def init_db():
    conn = sqlite3.connect('your_database.db')
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
    # Изменим логику для хранения города и страны
    cur.execute("INSERT OR REPLACE INTO users (user_id, city, country) VALUES (?, ?, ?)", (user_id, city, country))
    conn.commit()
    print(f"Город для пользователя {user_id} установлен как {city}, {country}")

def get_user_city(user_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT city, country FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0], row[1]  # Возвращаем и город, и страну
    return None, None


def get_all_users():
    cur.execute("SELECT user_id, city, country FROM users")
    users = cur.fetchall()
    # Используем tabulate для вывода красивой таблицы
    print(tabulate(users, headers=["User ID", "City", "Country"], tablefmt="pretty"))
    return users
