def route_agents(state):

    next_agent = state.get("next_agent")

    if next_agent == "sql_agent":
        return "sql"

    elif next_agent == "audit_agent":
        return "audit"

    elif next_agent == "forecast_agent":
        return "forecast"

    return "rag"