import React, { useState } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <div className="relative flex-1">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me anything..."
          disabled={isLoading}
          className="w-full rounded-lg bg-surface-secondary border border-dark-400 px-4 py-3
            text-sm text-white placeholder-gray-400
            focus:outline-none focus:ring-1 focus:ring-accent-500/50 focus:border-accent-500
            disabled:bg-surface-tertiary disabled:cursor-not-allowed
            transition-all duration-200 shadow-inner-sm"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-dark-400 border-t-accent-500" />
          </div>
        )}
      </div>
      <button
        type="submit"
        disabled={isLoading || !message.trim()}
        className={`rounded-lg px-4 py-3 text-sm font-medium
          transition-all duration-200 flex items-center gap-2 min-w-[4.5rem]
          ${isLoading || !message.trim()
            ? 'bg-surface-secondary text-gray-400 cursor-not-allowed border border-dark-400'
            : 'bg-accent-500 text-dark-800 hover:bg-accent-600 active:bg-accent-700 shadow-sm'
          }`}
      >
        {isLoading ? 'Sending' : 'Send'}
        {!isLoading && (
          <svg 
            className="w-4 h-4" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M13 7l5 5m0 0l-5 5m5-5H6" 
            />
          </svg>
        )}
      </button>
    </form>
  );
} 