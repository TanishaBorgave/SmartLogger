from datetime import datetime, timedelta


def get_log_count(conn, window_start, window_end):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
    """, (
        window_start.isoformat(),
        window_end.isoformat()
    ))

    return cursor.fetchone()[0]

def get_error_count(conn, window_start, window_end):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        AND severity = ?
    """, (
        window_start.isoformat(),
        window_end.isoformat(),
        "ERROR"
    ))

    return cursor.fetchone()[0]

def get_warning_count(conn, window_start, window_end):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        AND severity = ?
    """, (
        window_start.isoformat(),
        window_end.isoformat(),
        "WARN"
    ))

    return cursor.fetchone()[0]

def get_critical_count(conn, window_start, window_end):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        AND severity = ?
    """, (
        window_start.isoformat(),
        window_end.isoformat(),
        "CRITICAL"
    ))

    return cursor.fetchone()[0]

def get_avg_value_for_event(conn, window_start, window_end, event_type):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(value)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        AND event_type = ?
        AND value IS NOT NULL
    """, (
        window_start.isoformat(),
        window_end.isoformat(),
        event_type
    ))

    result = cursor.fetchone()[0]

    if result is None:
        return 0

    return result

def extract_features(conn, window_start, window_end):
    log_count = get_log_count(conn, window_start, window_end)
    error_count = get_error_count(conn, window_start, window_end)
    warning_count = get_warning_count(conn, window_start, window_end)
    critical_count = get_critical_count(conn, window_start, window_end)

    avg_db_slow_query = get_avg_value_for_event(
        conn,
        window_start,
        window_end,
        "DB_SLOW_QUERY"
    )

    avg_high_latency = get_avg_value_for_event(
        conn,
        window_start,
        window_end,
        "HIGH_LATENCY"
    )

    api_gateway_count = get_module_log_count(
        conn, window_start, window_end, "APIGateway"
    )

    auth_service_count = get_module_log_count(
        conn, window_start, window_end, "AuthService"
    )

    database_service_count = get_module_log_count(
        conn, window_start, window_end, "DatabaseService"
    )

    system_service_count = get_module_log_count(
        conn, window_start, window_end, "SystemService"
    )

    return [
        log_count,
        error_count,
        warning_count,
        critical_count,
        avg_db_slow_query,
        avg_high_latency,
        api_gateway_count,
        auth_service_count,
        database_service_count,
        system_service_count
    ]

def generate_windows(start_time, end_time, window_minutes=5):
    windows = []

    current = start_time

    while current < end_time:
        window_end = current + timedelta(minutes=window_minutes)

        if window_end > end_time:
            window_end = end_time

        windows.append((current, window_end))

        current = window_end

    return windows

def build_feature_dataset(conn, start_time, end_time):
    windows = generate_windows(
        start_time,
        end_time
    )

    dataset = []

    for window_start, window_end in windows:

        features = extract_features(
            conn,
            window_start,
            window_end
        )

        dataset.append({
            "window_start": window_start,
            "window_end": window_end,
            "features": features
        })

    return dataset

def get_module_log_count(conn, window_start, window_end, module):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        AND module = ?
    """, (
        window_start.isoformat(),
        window_end.isoformat(),
        module
    ))

    return cursor.fetchone()[0]

if __name__ == "__main__":
    import sqlite3

    conn = sqlite3.connect("../data/raw_logs.db")

    start_time = datetime(2026, 9, 11, 0, 0, 0)
    end_time = datetime(2026, 9, 12, 0, 0, 0)

    dataset = build_feature_dataset(
        conn,
        start_time,
        end_time
    )

    for row in dataset:
        if row["window_start"] == datetime(2026, 9, 11, 20, 0, 0):
         print("\nSilent failure window:")
         print(row)

    for row in dataset:
        if row["window_start"] == datetime(2026, 9, 11, 7, 0, 0):
            print("\nDegradation window (start):", row)
        if row["window_start"] == datetime(2026, 9, 11, 7, 15, 0):
            print("Degradation window (later):", row)

    for row in dataset:
        if row["window_start"] == datetime(2026, 9, 11, 2, 30, 0):
            print("\nSpike window:", row)

    print("Number of windows:", len(dataset))

    print("\nFirst 3 rows:")

    for row in dataset[:3]:
        print(row)

    conn.close()