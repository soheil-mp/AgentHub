import React from 'react';
import { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const formatTimestamp = (timestamp: string | undefined) => {
    if (!timestamp) return '';
    
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return '';
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-accent-500 text-white'
            : 'bg-surface-secondary border border-dark-400'
        }`}
      >
        <div className="text-sm">{message.content}</div>
        {message.timestamp && (
          <div className="text-xs mt-1 opacity-70">
            {formatTimestamp(message.timestamp)}
          </div>
        )}
      </div>
    </div>
  );
} 