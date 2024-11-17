import React, { useState, useRef, useEffect } from 'react';
import { Message } from '../../types';
import MessageList from './MessageList';
import ChatInput from './ChatInput';

interface ChatInterfaceProps {
  userId: string;
}

interface ApiError {
  message?: string;
  detail?: {
    message?: string;
  };
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    try {
      setIsLoading(true);
      
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      const response = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          user_id: userId,
          context: { locale: navigator.language },
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail?.message || 'An error occurred');
      }

      const data = await response.json();
      
      const lastAssistantMessage = data.messages
        .filter((msg: Message) => msg.role === 'assistant')
        .pop();
      
      if (lastAssistantMessage) {
        setMessages(prev => [...prev, {
          ...lastAssistantMessage,
          timestamp: new Date().toISOString(),
        }]);
      }
      
    } catch (err) {
      const error = err as ApiError;
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: error.message || error.detail?.message || 'Sorry, there was an error processing your message.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t">
        <ChatInput 
          onSend={sendMessage} 
          isLoading={isLoading} 
        />
      </div>
    </div>
  );
} 