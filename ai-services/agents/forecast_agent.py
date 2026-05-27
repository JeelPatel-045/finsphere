from core.llm import llm


def forecast_agent(financial_data: str) -> str:
    """Generate AI-driven financial forecasts from historical data."""
    prompt = f"""
You are a quantitative finance AI specialised in financial forecasting.

Based on the following historical financial data, provide:
- 6-month revenue forecast with confidence intervals
- Cashflow projections
- Key growth drivers and risk factors
- Actionable CFO-level recommendations

Financial Data:
{financial_data}
"""
    response = llm.invoke(prompt)
    return response.content
