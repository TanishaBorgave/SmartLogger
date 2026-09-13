import random
from datetime import datetime, timedelta

from config import MODULES, EVENT_TYPES


def determine_severity(severity_rule, value):

    if isinstance(severity_rule, str):
        return severity_rule

    for threshold, severity in severity_rule:

        if value <= threshold:
            return severity

    return "INFO"


def generate_baseline_log(timestamp):

    module = random.choice(MODULES)

    module_events = EVENT_TYPES[module]

    event_types = list(module_events.keys())

    weights = [
        module_events[event]["weight"]
        for event in event_types
    ]

    event_type = random.choices(
        event_types,
        weights=weights,
        k=1
    )[0]

    event_config = module_events[event_type]

    value_range = event_config["value_range"]

    if value_range is not None:

        value = random.randint(
            value_range[0],
            value_range[1]
        )

    else:

        value = None

    severity_rule = event_config["severity"]

    severity = determine_severity(
        severity_rule,
        value
    )

    message = event_config["message"]

    if value is not None:

        message = f"{message} | value={value}"

    return (
        timestamp,
        severity,
        module,
        event_type,
        message,
        value
    )


def format_log(log):

    timestamp, severity, module, event_type, message, value = log

    timestamp_str = timestamp.strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3]

    return (
        f"{timestamp_str} | "
        f"{severity} | "
        f"{module} | "
        f"{event_type} | "
        f"{message}"
    )


if __name__ == "__main__":

    start_time = datetime(
        2026,
        9,
        11,
        0,
        0,
        0
    )

    current_time = start_time

    logs = []

    for _ in range(500):

        log = generate_baseline_log(current_time)

        logs.append(log)

        gap = random.expovariate(2)

        current_time += timedelta(
            seconds=gap
        )


    with open("raw_logs.txt", "w") as file:

        for log in logs:

            formatted_log = format_log(log)

            file.write(formatted_log + "\n")

    print("Generated 500 logs.")
    print("Saved to raw_logs.txt")

    def inject_spike(start_time):

        logs = []

        count = random.randint(40, 60)

        duration = random.randint(120, 180)

        for _ in range(count):

            offset = random.uniform(0, duration)

            timestamp = start_time + timedelta(
            seconds=offset
            )

            value = random.randint(1000, 5000)

            log = (
            timestamp,
            "ERROR",
            "APIGateway",
            "REQUEST_TIMEOUT",
            f"API request timed out | value={value}",
            value
         )

            logs.append(log)

        logs.sort(key=lambda log: log[0])

        return logs


if __name__ == "__main__":

    start_time = datetime(
        2026,
        9,
        11,
        14,
        30,
        0
    )

    # spike_logs = inject_spike(start_time)

    # print("Number of spike logs:", len(spike_logs))

    # for log in spike_logs:
    #     print(log)

def inject_gradual_degradation(start_time):

    logs = []

    count = 250
    duration = 20 * 60

    for i in range(count):

        # timestamp
        progress = i / (count - 1)

        offset = progress * duration

        timestamp = start_time + timedelta(
            seconds=offset
        )

        # increasing value
        trend_value = 50 + progress * (600 - 50)

        # random variation
        jitter = random.uniform(-15, 15)

        value = trend_value + jitter

        log = (
            timestamp,
            "WARN",
            "DatabaseService",
            "DB_SLOW_QUERY",
            f"Query exceeded expected latency | value={value:.2f}",
            value
        )

        logs.append(log)

    # final failure
    deadlock_timestamp = start_time + timedelta(
        seconds=duration
    )

    deadlock_log = (
        deadlock_timestamp,
        "CRITICAL",
        "DatabaseService",
        "DB_DEADLOCK",
        "Database deadlock detected",
        None
    )

    logs.append(deadlock_log)

    return logs

start_time = datetime(
    2026,
    9,
    11,
    14,
    30,
    0
)

degradation_logs = inject_gradual_degradation(start_time)

#print("Number of degradation logs:", len(degradation_logs))

# for log in degradation_logs:
#     print(log)


def inject_cascading_failure(start_time):

    logs = []

    current_time = start_time

    # 1. Database connection is lost
    log = (
        current_time,
        "ERROR",
        "DatabaseService",
        "DB_CONN_LOST",
        "Connection to primary DB lost",
        None
    )

    logs.append(log)

    # 2. Database becomes slow
    slow_query_count = random.randint(5, 8)

    for _ in range(slow_query_count):

        current_time += timedelta(
            seconds=random.uniform(2, 5)
        )

        value = random.randint(150, 400)

        log = (
            current_time,
            "WARN",
            "DatabaseService",
            "DB_SLOW_QUERY",
            f"Query exceeded expected latency | value={value}",
            value
        )

        logs.append(log)

    # 3. API becomes slow
    latency_count = random.randint(5, 10)

    for _ in range(latency_count):

        current_time += timedelta(
            seconds=random.uniform(2, 5)
        )

        value = random.randint(300, 800)

        log = (
            current_time,
            "WARN",
            "APIGateway",
            "HIGH_LATENCY",
            f"Request latency is high | value={value}",
            value
        )

        logs.append(log)

    # 4. Final system failure
    current_time += timedelta(
        seconds=random.uniform(2, 5)
    )

    log = (
        current_time,
        "CRITICAL",
        "SystemService",
        "SERVICE_UNAVAILABLE",
        "Service is unavailable",
        None
    )

    logs.append(log)

    return logs

start_time = datetime(
    2026,
    9,
    11,
    15,
    0,
    0
)

cascade_logs = inject_cascading_failure(start_time)

# print("Number of cascade logs:", len(cascade_logs))

# for log in cascade_logs:
#     print(log)


def inject_retry_loop(start_time):
    logs = []
    current_time = start_time

    retry_count = random.randint(8, 15)


    for attempt in range(1, retry_count + 1):

        current_time += timedelta(
            seconds=random.uniform(0.5, 2)
        )

        log = (
            current_time,
            "WARN",
            "APIGateway",
            "RETRY_ATTEMPT",
            f"Retry attempt for failed API request | value={attempt}",
            attempt
        )

        logs.append(log)



    current_time += timedelta(
        seconds=random.uniform(0.5, 2)
    )

    log = (
        current_time,
        "ERROR",
        "APIGateway",
        "RETRY_EXHAUSTED",
        f"Maximum retry attempts exceeded | value={retry_count}",
        retry_count
    )

    logs.append(log)

    return logs

start_time = datetime(
    2026,
    9,
    11,
    15,
    30,
    0
)

retry_logs = inject_retry_loop(start_time)

# print("Number of retry logs:", len(retry_logs))

# for log in retry_logs:
#     print(log)

def inject_silent_failure(start_time):

    duration = timedelta(minutes=5)

    end_time = start_time + duration

    return {
        "start": start_time,
        "end": end_time,
        "type": "silent_failure"
    }

start_time = datetime(
    2026,
    9,
    11,
    16,
    0,
    0
)

silent_failure = inject_silent_failure(start_time)

print("Silent failure:")
print(silent_failure)



def generate_full_timeline():

    start_time = datetime(2026, 9, 11, 0, 0, 0)

    end_time = start_time + timedelta(hours=24)

    silent_time = start_time + timedelta(hours=20)

    logs = []
    silent_periods = []

    current_time = start_time

    while current_time < end_time:

        if silent_time <= current_time < silent_time + timedelta(minutes=5):
            current_time += timedelta(
                seconds=random.uniform(1, 3)
            )
            continue

        log = generate_baseline_log(current_time)
        logs.append(log)

        current_time += timedelta(
            seconds=random.uniform(1, 3)
        )

    # Generate anomaly injectors
    spike_time = start_time + timedelta(hours=2, minutes=30)
    degradation_time = start_time + timedelta(hours=7)
    cascade_time = start_time + timedelta(hours=11, minutes=30)
    retry_time = start_time + timedelta(hours=16)

    logs.extend(inject_spike(spike_time))
    logs.extend(inject_gradual_degradation(degradation_time))
    logs.extend(inject_cascading_failure(cascade_time))
    logs.extend(inject_retry_loop(retry_time))

    silent_failure = inject_silent_failure(silent_time)
    silent_periods.append(silent_failure)

    logs.sort(key=lambda x: x[0])

    return logs, silent_periods

if __name__ == "__main__":

    logs, silent_periods = generate_full_timeline()

    print("Total logs:", len(logs))
    print("Silent periods:", silent_periods)

    # Count important injected events
    spike_count = sum(
        1 for log in logs
        if log[3] == "REQUEST_TIMEOUT"
    )

    deadlock_count = sum(
        1 for log in logs
        if log[3] == "DB_DEADLOCK"
    )

    connection_lost_count = sum(
        1 for log in logs
        if log[3] == "DB_CONN_LOST"
    )

    service_unavailable_count = sum(
        1 for log in logs
        if log[3] == "SERVICE_UNAVAILABLE"
    )

    retry_exhausted_count = sum(
        1 for log in logs
        if log[3] == "RETRY_EXHAUSTED"
    )

    print("\nInjected anomaly counts:")
    print("REQUEST_TIMEOUT:", spike_count)
    print("DB_DEADLOCK:", deadlock_count)
    print("DB_CONN_LOST:", connection_lost_count)
    print("SERVICE_UNAVAILABLE:", service_unavailable_count)
    print("RETRY_EXHAUSTED:", retry_exhausted_count)