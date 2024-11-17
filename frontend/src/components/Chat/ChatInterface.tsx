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
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)]">
      {/* Chat Column */}
      <div className="flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-700">Chat Interface</h2>
          <p className="text-sm text-gray-500">
            {messages.length} messages • {isLoading ? 'Typing...' : 'Online'}
          </p>
        </div>

        {/* Messages Section */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50">
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Section */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <ChatInput 
            onSend={sendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>

      {/* Graph Column */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-700">Agent Workflow</h2>
              <p className="text-sm text-gray-500">
                Active: <span className="font-medium text-blue-600">{graphState.current_node}</span>
                {graphState.next_node && 
                  <span> → <span className="text-gray-600">{graphState.next_node}</span></span>
                }
              </p>
            </div>
            {graphState.requires_action && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                Requires Action
              </span>
            )}
          </div>
        </div>
        <div className="p-4 h-[calc(100%-5rem)]">
          <GraphVisualizer graphState={graphState} />
        </div>
      </div>
    </div>
  );
} 