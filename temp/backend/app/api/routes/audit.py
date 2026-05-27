from fastapi import APIRouter
from app.services.audit_service import detect_anomalies

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/anomalies")
def audit_transactions():
    results = detect_anomalies("datasets/finance/transactions.csv")

    return {
        "anomalies": results
    }