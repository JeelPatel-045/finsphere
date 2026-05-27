from sklearn.ensemble import IsolationForest
import pandas as pd


def detect_anomalies(data):

    df = pd.DataFrame(data)

    model = IsolationForest()

    predictions = model.fit_predict(df)

    df["anomaly"] = predictions

    return df.to_dict(orient="records")