from fastapi import APIRouter
from app.services.forecast_service import generate_forecast

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.get("/")
def forecast_data():
    results = generate_forecast("datasets/finance/revenue.csv")

    return {
        "forecast": results
    }