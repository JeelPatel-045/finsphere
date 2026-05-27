from models.risk_scoring import calculate_risk_score


def detect_risk_transactions(transactions):

    risky = []

    for tx in transactions:

        score = calculate_risk_score(tx)

        if score > 70:

            risky.append({
                "id": tx["id"],
                "risk_score": score,
                "reason": "High-value abnormal transaction"
            })

    return risky