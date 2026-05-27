from models.forecasting_model import forecast_revenue


def generate_forecast(data):

    forecast = forecast_revenue(data)

    return forecast