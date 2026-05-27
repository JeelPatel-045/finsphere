"""
LangGraph node wrappers — adapts each agent function to accept/return a state dict.
"""

import sys
import os

# Ensure ai-services/ root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.supervisor_agent import supervisor_agent
from agents.rag_agent         import rag_agent
from agents.sql_agent         import sql_agent
from agents.audit_agent       import audit_agent
from agents.forecast_agent    import forecast_agent


def supervisor_node(state: dict) -> dict:
    query    = state.get("query", "")
    response = supervisor_agent(query)
    state["supervisor_response"] = response
    return state


def rag_node(state: dict) -> dict:
    query  = state.get("query", "")
    docs   = rag_agent(query)
    state["rag_results"] = docs
    return state


def sql_node(state: dict) -> dict:
    query = state.get("query", "")
    sql   = sql_agent(query)
    state["sql_query"] = sql
    return state


def audit_node(state: dict) -> dict:
    data     = state.get("data", "")
    findings = audit_agent(data)
    state["audit_findings"] = findings
    return state


def forecast_node(state: dict) -> dict:
    data     = state.get("data", "")
    forecast = forecast_agent(data)
    state["forecast_result"] = forecast
    return state
