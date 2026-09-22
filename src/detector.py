from pprint import pprint

from sklearn.ensemble import IsolationForest
import json


def create_model():
    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )

    return model

def train_model(model, dataset):
    feature_vectors = [
        row["features"]
        for row in dataset
    ]

    model.fit(feature_vectors)

    return model

def detect_anomalies(model, dataset):
    feature_vectors = [
        row["features"]
        for row in dataset
    ]

    predictions = model.predict(feature_vectors)

    return predictions

def get_anomalous_windows(dataset, predictions, scores):
    anomalies = []

    for row, prediction, score in zip(dataset, predictions, scores):

        if prediction == -1:
            anomalies.append({
                "window_start": row["window_start"],
                "window_end": row["window_end"],
                "features": row["features"],
                "prediction": prediction,
                "score": score
            })

    return anomalies

def get_anomaly_scores(model, dataset):
    feature_vectors = [
        row["features"]
        for row in dataset
    ]

    scores = model.decision_function(feature_vectors)

    return scores

def evaluate_against_ground_truth(anomalies_filtered, ground_truth):
    results = []

    for gt in ground_truth:
        gt_start = datetime.fromisoformat(gt["start"])
        gt_end = datetime.fromisoformat(gt["end"])

        matched_windows = [
            a for a in anomalies_filtered
            if a["window_start"] <= gt_end
            and a["window_end"] >= gt_start
        ]

        results.append({
            "type": gt["type"],
            "detected": len(matched_windows) > 0,
            "matched_window_count": len(matched_windows)
        })

    return results

def count_false_positives(anomalies_filtered, ground_truth):
    false_positives = []

    for a in anomalies_filtered:
        is_true_positive = any(
            a["window_start"] <= datetime.fromisoformat(gt["end"])
            and a["window_end"] >= datetime.fromisoformat(gt["start"])
            for gt in ground_truth
        )

        if not is_true_positive:
            false_positives.append(a)

    return false_positives

if __name__ == "__main__":
    import sqlite3
    from datetime import datetime

    from features import build_feature_dataset

    conn = sqlite3.connect("../data/raw_logs.db")

    start_time = datetime(2026, 9, 11, 0, 0, 0)
    end_time = datetime(2026, 9, 12, 0, 0, 0)

    dataset = build_feature_dataset(
        conn,
        start_time,
        end_time
    )

    model = create_model()

    model = train_model(
        model,
        dataset
    )

    predictions = detect_anomalies(
    model,
    dataset
    )

    scores = get_anomaly_scores(model, dataset)

    anomalies = get_anomalous_windows(
    dataset,
    predictions,
    scores
    )

    anomalies_filtered = [
    a for a in anomalies
    if a["score"] < -0.02
]

    print("\nAnomalous windows:")

    for anomaly in anomalies:
        print(
        anomaly["window_start"],
        "→",
        anomaly["window_end"],
        anomaly["features"],
        "prediction =", anomaly["prediction"],
        "score =", anomaly["score"]
    )

    print(
    "\nNumber of anomalies after filtering:",
    len(anomalies_filtered)
    )   

    with open("ground_truth.json") as f:
        ground_truth = json.load(f)

    evaluation = evaluate_against_ground_truth(anomalies, ground_truth)

    print("\n--- Evaluation against ground truth ---")
    for result in evaluation:
        status = "DETECTED" if result["detected"] else "MISSED"
        print(f"{result['type']:25} {status}  (matched {result['matched_window_count']} window(s))")

    detected_count = sum(1 for r in evaluation if r["detected"])
    print(f"\nRecall: {detected_count}/{len(ground_truth)} injected anomalies detected")


    false_positives = count_false_positives(anomalies_filtered, ground_truth)
    print(
    f"False positives: {len(false_positives)} "
    f"out of {len(anomalies_filtered)} flagged windows"
    )

    true_positives = len(anomalies_filtered) - len(false_positives)

    print(
    f"Precision: {true_positives}/{len(anomalies_filtered)}"
    )

    print("Number of windows:", len(dataset))
    print("Model trained successfully.")

    conn.close()

