import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(csv_path: str):
    df = pd.read_csv(csv_path)

    model = IsolationForest(contamination=0.05)

    df["anomaly"] = model.fit_predict(df[["amount"]])

    anomalies = df[df["anomaly"] == -1]

    return anomalies.to_dict(orient="records")