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

def fetch_messages(
    limit: int,
    offset: int,
    from_msisdn: str | None = None,
    since: str | None = None,
    q: str | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    where_clauses = []
    params = []

    if from_msisdn:
        where_clauses.append("from_msisdn = ?")
        params.append(from_msisdn)

    if since:
        where_clauses.append("ts >= ?")
        params.append(since)

    if q:
        where_clauses.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    count_query = f"""
        SELECT COUNT(*) FROM messages
        {where_sql}
    """
    total = cursor.execute(count_query, params).fetchone()[0]

    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_sql}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """
    rows = cursor.execute(
        data_query,
        params + [limit, offset]
    ).fetchall()

    conn.close()

    data = [
        {
            "message_id": row["message_id"],
            "from": row["from_msisdn"],
            "to": row["to_msisdn"],
            "ts": row["ts"],
            "text": row["text"]
        }
        for row in rows
    ]

    return data, total

def fetch_stats():
    conn = get_connection()
    cursor = conn.cursor()

    total_messages = cursor.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    unique_senders = cursor.execute(
        "SELECT COUNT(DISTINCT from_msisdn) FROM messages"
    ).fetchone()[0]

    top_rows = cursor.execute("""
        SELECT from_msisdn, COUNT(*) as cnt
        FROM messages
        GROUP BY from_msisdn
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()

    first_ts = cursor.execute(
        "SELECT MIN(ts) FROM messages"
    ).fetchone()[0]

    last_ts = cursor.execute(
        "SELECT MAX(ts) FROM messages"
    ).fetchone()[0]

    conn.close()

    top_senders = [
        {"from": row["from_msisdn"], "count": row["cnt"]}
        for row in top_rows
    ]

    return {
        "total_messages": total_messages,
        "unique_senders": unique_senders,
        "top_senders": top_senders,
        "first_message_ts": first_ts,
        "last_message_ts": last_ts
    }
