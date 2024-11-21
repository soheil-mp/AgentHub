export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface GraphState {
  current_node: string;
  next_node: string;
  nodes: string[];
  edges: [string, string][];
  requires_action: boolean;
}

export interface ChatResponse {
  messages: Message[];
  requires_action: boolean;
  action_type?: string;
  graph_state?: GraphState;
} 