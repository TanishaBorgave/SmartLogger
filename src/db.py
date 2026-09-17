import sqlite3


def create_connection(db_path="../data/raw_logs.db"):

    conn = sqlite3.connect(db_path)

    return conn


def create_tables(conn):

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parsed_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            severity TEXT NOT NULL,
            module TEXT NOT NULL,
            event_type TEXT NOT NULL,
            message TEXT,
            value REAL
        )
    """)

    conn.commit()


def insert_logs(conn, parsed_logs):

    cursor = conn.cursor()

    rows = [
        (
            log[0].isoformat(),
            log[1],
            log[2],
            log[3],
            log[4],
            log[5]
        )
        for log in parsed_logs
        if log is not None
    ]

    cursor.executemany(
        """
        INSERT INTO parsed_logs
        (timestamp, severity, module, event_type, message, value)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows
    )

    conn.commit()