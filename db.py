import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PHOTOS_DIR = DATA_DIR / "photos"
DB_PATH = DATA_DIR / "bookshelf.db"


def _ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    PHOTOS_DIR.mkdir(exist_ok=True)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    _ensure_dirs()
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            date_finished TEXT NOT NULL,
            note TEXT,
            photo_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_book(title, author, date_finished, note, photo_filename):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO books (title, author, date_finished, note, photo_filename) VALUES (?, ?, ?, ?, ?)",
        (title, author, date_finished, note, photo_filename),
    )
    conn.commit()
    conn.close()


def get_all_books():
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM books ORDER BY date_finished DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_book(book_id):
    conn = _get_conn()
    row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_book(book_id):
    conn = _get_conn()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
