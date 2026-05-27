export interface AgentActivity {
  agent: string;
  action: string;
  timestamp: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ForecastData {
  month: string;
  revenue: number;
  forecast: number;
}

export interface RiskTransaction {
  id: string;
  vendor: string;
  amount: string;
  risk: string;
}