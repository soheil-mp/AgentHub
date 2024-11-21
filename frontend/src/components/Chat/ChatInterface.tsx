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
    <div className="grid grid-cols-1 lg:grid-cols-[1fr,400px] gap-6 h-[calc(100vh-8rem)]">
      {/* Left Column - Chat */}
      <div className="flex flex-col bg-surface-primary rounded-lg overflow-hidden shadow-lg border border-dark-400">
        {/* Chat Header */}
        <div className="px-4 py-3 bg-[#1e1e1e] border-b border-[#333333]">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-gray-200">Chat Interface</h2>
              <p className="text-xs text-gray-400 mt-0.5">
                {messages.length} messages • {isLoading ? 
                  <span className="text-[#06fdd8]">Agent is typing...</span> : 
                  <span className="text-[#06fdd8]">Online</span>
                }
              </p>
            </div>
            <button className="p-1.5 hover:bg-[#2a2a2a] rounded transition-colors">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Messages Section - Add smooth scroll shadow */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-[#1a1a1a]">
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input Section - Improved spacing and visual hierarchy */}
        <div className="p-4 bg-[#1e1e1e] border-t border-[#333333]">
          <ChatInput 
            onSend={sendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>

      {/* Right Column - Graph */}
      <div className="bg-surface-primary rounded-lg overflow-hidden shadow-lg border border-dark-400">
        <div className="px-4 py-3 bg-[#1e1e1e] border-b border-[#333333]">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-gray-200">Agent Workflow</h2>
              <p className="text-xs text-gray-400 mt-0.5">
                Active: <span className="font-medium text-[#06fdd8]">{graphState.current_node}</span>
                {graphState.next_node && 
                  <span> → <span className="text-gray-300">{graphState.next_node}</span></span>
                }
              </p>
            </div>
            {graphState.requires_action && (
              <span className="px-2.5 py-1 bg-[#2a2a2a] text-[#06fdd8] rounded text-xs font-medium border border-[#06fdd8]/20">
                Requires Action
              </span>
            )}
          </div>
        </div>
        <div className="h-[calc(100%-4.5rem)] bg-surface-primary">
          <GraphVisualizer graphState={graphState} />
        </div>
      </div>
    </div>
  );
} 