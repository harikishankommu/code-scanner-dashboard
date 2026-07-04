import sqlite3
from datetime import datetime

DB_NAME = "scan_history.db"


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TEXT,
            total_issues INTEGER,
            critical INTEGER,
            high INTEGER,
            medium INTEGER,
            low INTEGER
        )
    """)

    conn.commit()
    conn.close()


def save_scan(total_issues, counts):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scans (
            scan_time, total_issues, critical, high, medium, low
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_issues,
        counts["critical"],
        counts["high"],
        counts["medium"],
        counts["low"]
    ))

    conn.commit()
    conn.close()


def get_scan_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, scan_time, total_issues, critical, high, medium, low
        FROM scans
        ORDER BY id DESC
        LIMIT 5
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []

    for row in rows:
        history.append({
            "id": row[0],
            "scan_time": row[1],
            "total_issues": row[2],
            "critical": row[3],
            "high": row[4],
            "medium": row[5],
            "low": row[6]
        })

    return history

def clear_scan_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM scans")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='scans'")

    conn.commit()
    conn.close()