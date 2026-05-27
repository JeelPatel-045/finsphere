from langgraph.graph import StateGraph

from agents.audit_agent import audit_agent
from agents.report_agent import report_agent

workflow = StateGraph(dict)

workflow.add_node("audit_agent", audit_agent)
workflow.add_node("report_agent", report_agent)

workflow.set_entry_point("audit_agent")

workflow.add_edge("audit_agent", "report_agent")

graph = workflow.compile()