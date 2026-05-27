def calculate_risk_score(transaction):

    score = 0

    amount = transaction.get("amount", 0)

    if amount > 100000:
        score += 50

    if transaction.get("country") == "High Risk":
        score += 30

    if transaction.get("manual_entry"):
        score += 20

    return score