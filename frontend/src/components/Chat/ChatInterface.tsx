import React, { useRef, useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Message } from '../../types';
import { sendMessage } from '../../services/api';

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (content: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await sendMessage(content, userId);
      
      const updatedMessages = response.messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp || new Date().toISOString()
      }));
      
      setMessages(updatedMessages);
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[1fr,400px] gap-6 h-[calc(100vh-8rem)]">
      {/* Left Column - Chat */}
      <div className="flex flex-col bg-surface-primary rounded-lg overflow-hidden shadow-lg border border-dark-400">
        {/* Add error display */}
        {error && (
          <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/20 text-red-500 text-sm">
            {error}
          </div>
        )}
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
            onSend={handleSendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>
    </div>
  );
} 