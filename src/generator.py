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