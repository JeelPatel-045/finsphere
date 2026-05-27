from langgraph.graph import StateGraph

from agents.supervisor_agent import supervisor_agent
from agents.rag_agent import rag_agent
from agents.sql_agent import sql_agent

workflow = StateGraph(dict)

workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("rag_agent", rag_agent)
workflow.add_node("sql_agent", sql_agent)

workflow.set_entry_point("supervisor")

workflow.add_edge("supervisor", "rag_agent")
workflow.add_edge("supervisor", "sql_agent")

graph = workflow.compile()