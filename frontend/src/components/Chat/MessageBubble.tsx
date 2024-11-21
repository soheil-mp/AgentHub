import React from 'react';
import { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
  isUser: boolean;
}

export default function MessageBubble({ message, isUser }: MessageBubbleProps) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} group`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-[#1e1e1e] flex items-center justify-center mr-2 border border-[#333333]">
          <span className="text-base">🤖</span>
        </div>
      )}
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2.5
          ${isUser 
            ? 'bg-[#1e1e1e] border border-[#333333] text-white'
            : 'bg-[#1e1e1e] border border-[#333333] text-gray-100'
          }`}
      >
        <div className="flex flex-col gap-1">
          <p className="text-sm whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-gray-400">
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
        </div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-[#1e1e1e] border border-[#333333] flex items-center justify-center ml-2">
          <span className="text-xs text-gray-200 font-medium">You</span>
        </div>
      )}
    </div>
  );
} 