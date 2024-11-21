export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  messages: Message[];
  requires_action: boolean;
  action_type?: string;
} 