from datetime import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv
from streamlit import json
import json

from detector import run_detection


load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


def generate_rca(prompt):
    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a system log analysis assistant. "
                    "Return only the final RCA answer. "
                    "Do not output reasoning, thinking, or analysis traces."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=800,
        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }
    )

    return response.choices[0].message.content

def build_context(window_start, window_end, conn):

    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, severity, module, event_type, message, value
        FROM parsed_logs
        WHERE timestamp >= ?
        AND timestamp < ?
        ORDER BY timestamp
    """, (
        window_start.isoformat(),
        window_end.isoformat()
    ))

    logs = cursor.fetchall()

    # Keep only a representative sample
    sampled_logs = logs[:40]

    # Severity counts
    severity_counts = {
        "ERROR": 0,
        "CRITICAL": 0,
        "WARN": 0
    }

    for log in logs:

        severity = log[1]

        if severity in severity_counts:
            severity_counts[severity] += 1

    # Modules involved
    modules = sorted(
        set(log[2] for log in logs)
    )

    # Event types involved
    event_types = sorted(
        set(log[3] for log in logs)
    )

    # Convert logs back into readable lines
    log_lines = []

    for log in sampled_logs:

        timestamp = log[0]
        severity = log[1]
        module = log[2]
        event_type = log[3]
        message = log[4]
        value = log[5]

        line = (
            f"{timestamp} | "
            f"{severity} | "
            f"{module} | "
            f"{event_type} | "
            f"{message}"
        )

        if value is not None:
            line += f" | value={value}"

        log_lines.append(line)

    return {
        "start": window_start.isoformat(),
        "end": window_end.isoformat(),
        "log_lines": "\n".join(log_lines),
        "severity_counts": severity_counts,
        "modules": modules,
        "event_types": event_types,
        "log_count": len(logs)
    }

def build_prompt(context):
    prompt = f"""
You are a system log analysis assistant helping engineers understand anomalies flagged by an automated detection system.

An unsupervised anomaly detector (Isolation Forest) flagged the following time window as statistically abnormal compared to the system's normal behavior.

Time window:
{context["start"]} to {context["end"]}

Total logs in window:
{context["log_count"]}

Severity counts:
{context["severity_counts"]}

Modules involved:
{context["modules"]}

Event types:
{context["event_types"]}

Log excerpt:
{context["log_lines"]}

Explain:
1. What happened during this window?
2. What is the most likely root cause?
3. Which specific logs or patterns support your conclusion?
4. What should an engineer investigate next?
5. Your confidence level (high/medium/low), and whether the evidence is ambiguous or insufficient for a confident diagnosis.

Keep the explanation concise, specific to the evidence provided, and evidence-based. Do not speculate beyond what the logs support.
"""
    return prompt

if __name__ == "__main__":

    import sqlite3

    conn = sqlite3.connect("../data/raw_logs.db")

    start_time = datetime(2026, 9, 11, 0, 0, 0)
    end_time = datetime(2026, 9, 12, 0, 0, 0)

    dataset, predictions, anomalies, anomalies_filtered = run_detection(
        conn,
        start_time,
        end_time
    )

    print("\n--- DETECTED ANOMALOUS WINDOWS FOR RCA ---")

    for anomaly in anomalies_filtered:
        print(
            anomaly["window_start"],
            "→",
            anomaly["window_end"],
            "score =",
            anomaly["score"]
        )

    # Store all RCA results here
    rca_results = []

    # Generate RCA for every detected anomaly
    for i, anomaly in enumerate(anomalies_filtered, start=1):

        window_start = anomaly["window_start"]
        window_end = anomaly["window_end"]

        context = build_context(
            window_start,
            window_end,
            conn
        )

        prompt = build_prompt(context)

        rca_result = generate_rca(prompt)

        print(f"\n--- RCA RESULT {i} ---")
        print(rca_result)

        # Add this RCA to the results list
        rca_results.append({
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "anomaly_score": anomaly["score"],
            "rca": rca_result
        })

    # Save all RCA results to one JSON file
    with open("../data/rca_results.json", "w") as f:
        json.dump(rca_results, f, indent=4)

    print("\nRCA results saved to ../data/rca_results.json")

    conn.close()