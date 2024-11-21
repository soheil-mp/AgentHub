interface ImportMetaEnv {
  VITE_API_URL: string;
  // Add other env variables here if needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatResponse {
  messages: Message[];
  requires_action: boolean;
  action_type?: string;
  graph_state?: {
    current_node: string;
    next_node: string;
    nodes: string[];
    edges: [string, string][];
    requires_action: boolean;
  };
}

const API_URL = import.meta.env.VITE_API_URL || 'http://api:8000';

export const sendMessage = async (message: string, userId: string): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: [{ role: 'user', content: message }],
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}; 