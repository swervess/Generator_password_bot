import sqlite3
from datetime import datetime

DB_NAME = "passwords.db"


def init_db():
    """Инициализация базы данных: создание таблиц, если они не существуют."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_name TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()


def register_user(user_id: int, username: str, first_name: str, last_name: str):
    """Регистрация нового пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registered_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, first_name, last_name, datetime.now()))
    conn.commit()
    conn.close()


def save_password(user_id: int, service_name: str, password: str) -> bool:
    """Сохранение пароля для пользователя."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO passwords (user_id, service_name, password, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, service_name, password, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Ошибка сохранения пароля: {e}")
        return False
    finally:
        conn.close()


def get_user_passwords(user_id: int):
    """Получение всех сохранённых паролей пользователя."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, service_name, password, created_at
        FROM passwords
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    passwords = cursor.fetchall()
    conn.close()
    return passwords


def delete_password(password_id: int, user_id: int) -> bool:
    """Удаление пароля по ID (проверка принадлежности пользователю)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE id = ? AND user_id = ?", (password_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted