from datetime import datetime
from db import create_connection, create_tables, insert_logs

def parse_log_line(line):
    try:
        parts = line.strip().split(" | ")

        timestamp = datetime.strptime(
            parts[0],
            "%Y-%m-%d %H:%M:%S.%f"
        )

        severity = parts[1]
        module = parts[2]
        event_type = parts[3]

        value = None

        message_parts = parts[4:]

        if message_parts and message_parts[-1].startswith("value="):

            value = float(
                message_parts[-1].split("=")[1]
            )

            message = " | ".join(
                message_parts[:-1]
            )

        else:

            message = " | ".join(
                message_parts
            )

        return (
            timestamp,
            severity,
            module,
            event_type,
            message,
            value
        )

    except (IndexError, ValueError):
        return None

if __name__ == "__main__":

    parsed_logs = []
    none_count = 0
    total_count = 0

    with open("raw_logs.txt", "r") as file:

        for line in file:

            total_count += 1

            parsed = parse_log_line(line)

            if parsed is None:
                none_count += 1
            else:
                parsed_logs.append(parsed)

    print("Total lines:", total_count)
    print("Unparseable lines:", none_count)

    print(
        "Parse success rate:",
        ((total_count - none_count) / total_count) * 100,
        "%"
    )

    print("\nFirst 5 parsed logs:")

    for log in parsed_logs[:5]:
        print(log)

    # Connect to SQLite database
    conn = create_connection()

    # Create table
    create_tables(conn)

    # Insert parsed logs
    insert_logs(conn, parsed_logs)

    # Close database
    conn.close()

    print("\nLogs successfully inserted into SQLite.")