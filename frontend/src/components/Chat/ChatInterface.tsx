import React, { useRef, useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import GraphVisualizer from '../Graph/GraphVisualizer';
import { Message, GraphState } from '../../types';

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [graphState, setGraphState] = useState<GraphState>({
    current_node: 'ROUTER',
    next_node: '',
    nodes: ['ROUTER', 'PRODUCT', 'TECHNICAL', 'CUSTOMER_SERVICE', 'HUMAN'],
    edges: [
      ['ROUTER', 'PRODUCT'],
      ['ROUTER', 'TECHNICAL'],
      ['ROUTER', 'CUSTOMER_SERVICE'],
      ['ROUTER', 'HUMAN'],
      ['PRODUCT', 'CUSTOMER_SERVICE'],
      ['PRODUCT', 'TECHNICAL'],
      ['TECHNICAL', 'PRODUCT'],
      ['TECHNICAL', 'HUMAN'],
      ['CUSTOMER_SERVICE', 'HUMAN'],
      ['CUSTOMER_SERVICE', 'PRODUCT'],
      ['HUMAN', 'ROUTER']
    ],
    requires_action: false
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessage = async (content: string) => {
    try {
      setIsLoading(true);
      
      const newMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, newMessage]);

      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, newMessage].map(({ role, content }) => ({ role, content })),
          user_id: userId,
        }),
      });

      const data = await response.json();
      
      if (data.messages) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.messages[data.messages.length - 1].content,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, assistantMessage]);
      }

      // Update graph state if provided in response
      if (data.graph_state) {
        setGraphState(data.graph_state);
      }

    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      {/* Graph Visualization Section */}
      <div className="p-4 border-b">
        <GraphVisualizer graphState={graphState} />
      </div>
      
      {/* Messages Section */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Section */}
      <div className="p-4 border-t">
        <ChatInput 
          onSend={sendMessage} 
          isLoading={isLoading} 
        />
      </div>
    </div>
  );
} 