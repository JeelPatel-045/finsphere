from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpis")
def get_kpis():
    return {
        "revenue": 1250000,
        "expenses": 720000,
        "profit": 530000,
        "high_risk_transactions": 18
    }