from prophet import Prophet
import pandas as pd


def forecast_revenue(data):

    df = pd.DataFrame(data)

    model = Prophet()

    model.fit(df)

    future = model.make_future_dataframe(periods=30)

    forecast = model.predict(future)

    return forecast.tail(30).to_dict(orient="records")