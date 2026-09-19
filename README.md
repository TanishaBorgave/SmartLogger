# SmartLog Analyzer

An intelligent log anomaly detection and root cause analysis system. SmartLog Analyzer parses raw system/application logs, engineers time-windowed statistical and sequence-based features, detects anomalies using unsupervised machine learning, and — going a step beyond simple classification — uses an LLM (NVIDIA Nemotron) to generate a human-readable root cause explanation for each flagged anomaly.

> Most monitoring tools tell you *something is wrong*. SmartLog Analyzer tries to tell you *why*.

## Why this project exists

Traditional log monitoring relies on static threshold alerts ("page me if errors > 50/min"). These break down in two ways: they miss slow-building degradation that never crosses a fixed line, and they don't adapt as a system's normal behavior changes over time. They also stop at detection — a human still has to read through the logs and figure out what actually happened.

SmartLog Analyzer addresses both problems:
1. **Detection** — learns what "normal" looks like directly from the data (unsupervised) instead of relying on hand-set thresholds, so it adapts to the system's actual behavior and catches multi-dimensional patterns a single rule would miss.
2. **Explanation** — once an anomaly is flagged, the relevant log context is passed to an LLM, which produces a plain-language root cause hypothesis, the likely sequence of events, and a suggested next step — turning a raw alert into something a human can act on immediately.

## What it detects

- Sudden error/failure spikes
- Gradual performance degradation (e.g., slowly rising query latency ending in failure)
- Cascading failures across dependent services
- Repeated failure / retry-storm patterns
- Silent failures (unexpected absence of expected log activity)

## Architecture

```
Raw Logs
   │
   ▼
Log Parser (regex-based, drain3 explored for template mining)
   │
   ▼
Feature Extraction (time-windowed statistical + sequence features)
   │
   ▼
Anomaly Detection (Isolation Forest, benchmarked against a statistical/EWMA baseline)
   │
   ▼
Severity Classification
   │
   ▼
Root Cause Analysis (NVIDIA Nemotron via NIM API)
   │
   ▼
Dashboard (Streamlit)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Core pipeline | Python |
| Data processing / feature engineering | Pandas, NumPy |
| Anomaly detection | Scikit-learn (Isolation Forest) |
| Log template mining | drain3 |
| Root cause analysis | NVIDIA Nemotron (via NIM API, OpenAI-compatible) |
| Persistence | SQLite |
| Dashboard | Streamlit |

## How the synthetic dataset works

Real labeled anomaly data is hard to come by (and rarely public), so this project includes a synthetic log generator that simulates a realistic backend system — an API gateway, auth service, database service, and system/infra service — producing both routine baseline traffic and five deliberately injected anomaly scenarios:

| Scenario | Description |
|---|---|
| Spike | Sudden burst of request timeouts over a short window |
| Gradual degradation | Query latency climbing steadily over ~20 minutes, ending in a deadlock |
| Cascading failure | A DB connection loss triggering slow queries → high latency → service unavailability, across modules |
| Retry loop | Repeated auth failures culminating in a privilege escalation attempt |
| Silent failure | An unexpected absence of logs from a normally active module |

Every injected scenario is recorded with its exact time window in `ground_truth.json`, which is used purely for evaluating detector performance after the fact — the detection pipeline never sees these labels, consistent with the unsupervised approach.

## Project structure

```
smartlog-analyzer/
├── data/                  # SQLite database
├── src/
│   ├── generator.py       # synthetic log + anomaly generator
│   ├── parser.py          # raw log → structured record parser
│   ├── db.py               # SQLite schema + insert helpers
│   ├── features.py        # time-windowed feature extraction
│   ├── detector.py        # Isolation Forest + statistical baseline
│   ├── rca.py              # LLM-based root cause analysis
│   └── config.py           # severity levels, modules, event types
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone <repo-url>
cd smartlog-analyzer
python -m venv smartlog_env
source smartlog_env/bin/activate    # Windows: smartlog_env\Scripts\activate
pip install -r requirements.txt
```

Root cause analysis requires an NVIDIA API key (free tier available at [build.nvidia.com](https://build.nvidia.com)):
```bash
export NVIDIA_API_KEY="nvapi-..."
```

## Usage

```bash
# 1. Generate a synthetic 24-hour log dataset with injected anomalies
python src/generator.py

# 2. Parse raw logs and load into SQLite
python src/parser.py

# 3. Extract features and run anomaly detection
python src/detector.py

# 4. Launch the dashboard
streamlit run dashboard/app.py
```

## Validation

Detector performance is evaluated by comparing flagged anomaly windows against the known injection windows in `ground_truth.json`, reporting precision and recall per anomaly type. Results are documented in [`RESULTS.md`](RESULTS.md) 

