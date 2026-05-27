"""
Main LangGraph workflow — routes queries through the supervisor to specialist agents.
Run from the ai-services/ directory so that all local imports resolve correctly.
"""

import sys
import os

# Ensure ai-services/ root is on the path so local packages (agents/, core/) resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from langgraph.graph import StateGraph

# Import nodes from the local langgraph/nodes.py (not the installed package)
from langgraph.nodes import (   # noqa: E402  (after sys.path fix)
    supervisor_node,
    rag_node,
    sql_node,
    audit_node,
    forecast_node,
)

from langgraph.edges import route_agents  # noqa: E402

# ── Build graph ───────────────────────────────────────────────────────────────

workflow = StateGraph(dict)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("rag",        rag_node)
workflow.add_node("sql",        sql_node)
workflow.add_node("audit",      audit_node)
workflow.add_node("forecast",   forecast_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges(
    "supervisor",
    route_agents,
    {
        "sql":      "sql",
        "audit":    "audit",
        "forecast": "forecast",
        "rag":      "rag",
    },
)

graph = workflow.compile()
