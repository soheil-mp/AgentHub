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
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-2">
          <span className="text-lg">🤖</span>
        </div>
      )}
      <div
        className={`max-w-[70%] rounded-2xl px-4 py-2.5 shadow-sm transition-all
          ${isUser 
            ? 'bg-blue-500 text-white group-hover:bg-blue-600' 
            : 'bg-white text-gray-900 group-hover:bg-gray-50 border border-gray-200'
          }`}
      >
        <div className="flex flex-col gap-1">
          <div className="flex items-start gap-2">
            <div>
              <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs ${isUser ? 'text-blue-200' : 'text-gray-500'}`}>
                  {new Date(message.timestamp).toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
                {isUser && (
                  <span className="text-xs text-blue-200">
                    • You
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center ml-2">
          <span className="text-sm text-white font-medium">You</span>
        </div>
      )}
    </div>
  );
} 