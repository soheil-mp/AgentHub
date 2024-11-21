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
  timestamp?: string;
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

export const sendMessage = async (message: string, userId: string): Promise<ChatResponse> => {
  try {
    const payload = {
      messages: [{
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }],
      user_id: userId,
      context: {}
    };

    console.log('Sending request:', payload);

    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': window.location.origin
      },
      credentials: 'include',
      body: JSON.stringify(payload),
    });

    console.log('Response status:', response.status);

    // First try to get the response text
    const responseText = await response.text();
    console.log('Raw response:', responseText);

    let data;
    try {
      // Then try to parse it as JSON
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('Failed to parse JSON response:', parseError);
      console.error('Raw response was:', responseText);
      throw new Error(`Invalid JSON response from server: ${responseText}`);
    }

    if (!response.ok) {
      console.error('API error response:', data);
      throw new Error(
        `API error: ${response.status}${data ? ' - ' + JSON.stringify(data) : ''}`
      );
    }

    console.log('Parsed response data:', data);
    return data;
  } catch (error) {
    console.error('Error in sendMessage:', error);
    throw error;
  }
};

export const getGraphStructure = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/chat/graph/structure`, {
      headers: {
        'Accept': 'application/json',
        'Origin': window.location.origin
      },
      credentials: 'include'
    });
    
    // First get the response text
    const responseText = await response.text();
    console.log('Raw graph response:', responseText);

    let data;
    try {
      // Then try to parse it as JSON
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('Failed to parse JSON response:', parseError);
      console.error('Raw response was:', responseText);
      throw new Error(`Invalid JSON response from server: ${responseText}`);
    }

    if (!response.ok) {
      console.error('API error response:', data);
      throw new Error(
        `API error: ${response.status}${data ? ' - ' + JSON.stringify(data) : ''}`
      );
    }

    return data;
  } catch (error) {
    console.error('Error fetching graph structure:', error);
    throw error;
  }
}; 