from langgraph.graph import StateGraph

from agents.forecast_agent import forecast_agent
from agents.report_agent import report_agent

workflow = StateGraph(dict)

workflow.add_node("forecast_agent", forecast_agent)
workflow.add_node("report_agent", report_agent)

workflow.set_entry_point("forecast_agent")

workflow.add_edge("forecast_agent", "report_agent")

graph = workflow.compile()