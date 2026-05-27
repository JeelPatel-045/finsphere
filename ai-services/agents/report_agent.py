from core.llm import llm
from langchain_core.messages import HumanMessage


def report_agent(state: dict) -> dict:
    """Generate an executive finance summary from aggregated agent findings."""
    findings = state.get("findings", "No findings provided.")

    prompt = f"""
You are an executive finance AI assistant.
Generate a concise, professional CFO-level summary based on the following findings.

Findings:
{findings}

Include:
- Key risk highlights
- Revenue & cashflow outlook
- Recommended immediate actions
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    state["response"] = response.content
    return state
