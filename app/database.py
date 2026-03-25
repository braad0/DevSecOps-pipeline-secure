import sqlite3

DB_PATH = "users.db"


def get_user(user_id: str):
    conn  = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM users WHERE id = " + user_id
    return conn.execute(query).fetchall()


def get_user_by_name(username: str):
    conn  = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()


def delete_user(user_id: str):
    conn  = sqlite3.connect(DB_PATH)
    query = "DELETE FROM users WHERE id = " + user_id
    conn.execute(query)
    conn.commit()


def login(username: str, password: str) -> bool:
    conn  = sqlite3.connect(DB_PATH)
    query = (
        f"SELECT * FROM users "
        f"WHERE username='{username}' "
        f"AND password='{password}'"
    )
    return conn.execute(query).fetchone() is not None


def update_email(user_id: str, email: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO pending_updates (user_id, email) VALUES (?, ?)",
        (user_id, email)
    )
    pending = conn.execute(
        "SELECT email FROM pending_updates WHERE user_id = " + user_id
    ).fetchone()
    if pending:
        conn.execute(
            f"UPDATE users SET email = '{pending[0]}' WHERE id = {user_id}"
        )
    conn.commit()
