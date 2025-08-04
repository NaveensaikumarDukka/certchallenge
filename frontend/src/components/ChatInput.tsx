'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Smile, Mic } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading?: boolean;
  placeholder?: string;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder = "Type your message...",
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading || disabled) return;

    const trimmedMessage = message.trim();
    setMessage('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    await onSendMessage(trimmedMessage);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  const isSendDisabled = !message.trim() || isLoading || disabled;

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onCompositionStart={handleCompositionStart}
          onCompositionEnd={handleCompositionEnd}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full resize-none rounded-2xl border border-neutral-200 bg-white/90 backdrop-blur-sm px-5 py-4 pr-32 text-sm leading-relaxed focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-professional"
          style={{ minHeight: '56px', maxHeight: '140px' }}
          rows={1}
        />
        
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
          {/* Voice Button */}
          <button
            type="button"
            disabled={disabled}
            className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg"
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>
          
          {/* Emoji Button */}
          <button
            type="button"
            disabled={disabled}
            className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg"
            title="Add emoji"
          >
            <Smile className="w-4 h-4" />
          </button>
          
          {/* Attachment Button */}
          <button
            type="button"
            disabled={disabled}
            className="p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg"
            title="Attach file"
          >
            <Paperclip className="w-4 h-4" />
          </button>
          
          {/* Send Button */}
          <button
            type="submit"
            disabled={isSendDisabled}
            className={`p-3 rounded-xl transition-all duration-200 ${
              isSendDisabled
                ? 'text-neutral-300 cursor-not-allowed bg-neutral-100'
                : 'text-white gradient-primary hover:shadow-professional-lg hover:scale-105 shadow-professional'
            }`}
            title="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Character count and typing indicator */}
      <div className="mt-3 flex items-center justify-between">
        {message.length > 0 && (
          <div className="text-xs text-neutral-500 font-medium">
            {message.length} characters
          </div>
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center space-x-2 text-sm text-neutral-500">
            <div className="loading-dots">
              <div></div>
              <div></div>
              <div></div>
            </div>
            <span className="font-medium">Processing your request...</span>
          </div>
        )}
      </div>
      
      {/* Quick tips */}
      {message.length === 0 && !isLoading && (
        <div className="mt-3 text-xs text-neutral-400 text-center">
          💡 Try asking about investment strategies, portfolio analysis, or market trends
        </div>
      )}
    </form>
  );
};

export default ChatInput; 