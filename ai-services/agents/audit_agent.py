from core.llm import llm


def audit_agent(data: str) -> str:
    """Analyse financial data for anomalies, fraud, and compliance violations."""
    prompt = f"""
You are an AI financial auditor with expertise in fraud detection and compliance.

Analyse the following financial data and report:
- Detected fraud patterns or suspicious behaviour
- Duplicate invoice instances
- High-risk transactions
- SOX / IFRS compliance violations
- Recommended corrective actions

Financial Data:
{data}
"""
    response = llm.invoke(prompt)
    return response.content
