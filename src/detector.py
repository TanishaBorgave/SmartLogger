from sklearn.ensemble import IsolationForest


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

    print("\nNumber of anomalies:", list(predictions).count(-1))

    print("Number of windows:", len(dataset))
    print("Model trained successfully.")

    conn.close()

