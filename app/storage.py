import sqlite3
from datetime import datetime
from typing import Optional, Tuple

DB_PATH = "data/app.db"


def get_connection():
    """
    Create and return a SQLite connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create messages table if it does not exist
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn   TEXT NOT NULL,
            ts          TEXT NOT NULL,
            text        TEXT,
            created_at  TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_message(
    message_id: str,
    from_msisdn: str,
    to_msisdn: str,
    ts: str,
    text: Optional[str]
) -> bool:
    """
    Insert a message into DB.

    Returns:
        True  -> inserted successfully
        False -> duplicate message_id
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO messages (
                message_id, from_msisdn, to_msisdn, ts, text, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message_id,
            from_msisdn,
            to_msisdn,
            ts,
            text,
            datetime.utcnow().isoformat() + "Z"
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # message_id already exists (duplicate)
        return False

    finally:
        conn.close()
