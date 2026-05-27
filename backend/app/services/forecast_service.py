import pandas as pd
from prophet import Prophet


def generate_forecast(csv_path: str):
    df = pd.read_csv(csv_path)

    df.columns = ["ds", "y"]

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=6, freq="M")
    forecast = model.predict(future)

    return forecast[["ds", "yhat"]].tail(6).to_dict(orient="records")