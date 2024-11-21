import React from 'react';
import { Message } from '../../types';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <MessageBubble
          key={index}
          message={message}
          isUser={message.role === 'user'}
        />
      ))}
    </div>
  );
} 