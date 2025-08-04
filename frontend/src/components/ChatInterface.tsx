'use client';

import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, RefreshCw, Trash2, Bot, User, AlertCircle, Settings, Sparkles } from 'lucide-react';
import { useChat } from '@/hooks/useChat';
import Message from './Message';
import ChatInput from './ChatInput';
import LoadingSpinner from './LoadingSpinner';
import ToolSelector from './ToolSelector';
import SettingsModal from './SettingsModal';

const ChatInterface: React.FC = () => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  const {
    messages,
    isLoading,
    error,
    tools_used,
    confidence,
    sendMessage,
    clearMessages,
    retryLastMessage,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleClearChat = () => {
    clearMessages();
  };

  const handleRetry = async () => {
    await retryLastMessage();
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
      {/* Header */}
      <div className="gradient-card border-professional-light shadow-professional px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 gradient-primary rounded-xl flex items-center justify-center shadow-professional-lg">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 tracking-tight">
                Wealth Advisor AI
              </h1>
              <p className="text-sm text-neutral-600 font-medium">
                Your intelligent financial companion
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {tools_used.length > 0 && (
              <div className="flex items-center space-x-2 bg-white/60 backdrop-blur-sm px-3 py-2 rounded-lg border-professional-light">
                <span className="text-xs text-neutral-600 font-medium">Active Tools:</span>
                <div className="flex items-center space-x-1">
                  {tools_used.map((tool) => (
                    <span
                      key={tool}
                      className={`tool-badge ${tool.toLowerCase()}`}
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {confidence > 0 && (
              <div className="flex items-center space-x-2 bg-white/60 backdrop-blur-sm px-3 py-2 rounded-lg border-professional-light">
                <span className="text-xs text-neutral-600 font-medium">Confidence:</span>
                <span className="text-xs font-semibold text-emerald-600">
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            )}
            
            <button
              onClick={() => setIsSettingsOpen(true)}
              className="p-2.5 text-neutral-500 hover:text-neutral-700 hover:bg-white/60 transition-all duration-200 rounded-lg border-professional-light"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden">
        <div
          ref={chatContainerRef}
          className="h-full overflow-y-auto px-6 py-6 space-y-6"
        >
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col items-center justify-center h-full text-center px-4"
              >
                <div className="w-24 h-24 gradient-primary rounded-full flex items-center justify-center mb-8 shadow-professional-lg">
                  <Sparkles className="w-12 h-12 text-white" />
                </div>
                <h2 className="text-4xl font-bold text-neutral-900 mb-4 tracking-tight">
                  Welcome to Wealth Advisor AI
                </h2>
                <p className="text-neutral-600 max-w-lg text-lg leading-relaxed mb-10">
                  I'm your AI-powered financial advisor, ready to help you with investment strategies, 
                  portfolio management, retirement planning, and market analysis.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl w-full">
                  <button
                    onClick={() => sendMessage("What are the best investment strategies for retirement planning?")}
                    className="p-6 text-left gradient-card rounded-2xl border-professional-light hover:border-blue-300 hover:shadow-professional-lg transition-all duration-300 hover:scale-105 group"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                        <span className="text-blue-600 font-bold text-sm">💰</span>
                      </div>
                      <div className="font-semibold text-neutral-900 text-lg">Retirement Planning</div>
                    </div>
                    <div className="text-sm text-neutral-600">Smart investment strategies for your golden years</div>
                  </button>
                  <button
                    onClick={() => sendMessage("How should I diversify my investment portfolio?")}
                    className="p-6 text-left gradient-card rounded-2xl border-professional-light hover:border-emerald-300 hover:shadow-professional-lg transition-all duration-300 hover:scale-105 group"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-emerald-100 rounded-lg flex items-center justify-center group-hover:bg-emerald-200 transition-colors">
                        <span className="text-emerald-600 font-bold text-sm">📊</span>
                      </div>
                      <div className="font-semibold text-neutral-900 text-lg">Portfolio Diversification</div>
                    </div>
                    <div className="text-sm text-neutral-600">Risk management and asset allocation strategies</div>
                  </button>
                  <button
                    onClick={() => sendMessage("What are the current market trends for tech stocks?")}
                    className="p-6 text-left gradient-card rounded-2xl border-professional-light hover:border-purple-300 hover:shadow-professional-lg transition-all duration-300 hover:scale-105 group"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                        <span className="text-purple-600 font-bold text-sm">📈</span>
                      </div>
                      <div className="font-semibold text-neutral-900 text-lg">Market Analysis</div>
                    </div>
                    <div className="text-sm text-neutral-600">Current trends and market insights</div>
                  </button>
                  <button
                    onClick={() => sendMessage("What tax considerations should I keep in mind for investments?")}
                    className="p-6 text-left gradient-card rounded-2xl border-professional-light hover:border-amber-300 hover:shadow-professional-lg transition-all duration-300 hover:scale-105 group"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center group-hover:bg-amber-200 transition-colors">
                        <span className="text-amber-600 font-bold text-sm">📋</span>
                      </div>
                      <div className="font-semibold text-neutral-900 text-lg">Tax Planning</div>
                    </div>
                    <div className="text-sm text-neutral-600">Tax-efficient investment strategies</div>
                  </button>
                </div>
              </motion.div>
            )}

            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Message message={message} />
              </motion.div>
            ))}

            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center space-x-4 p-6 gradient-card rounded-2xl border-professional-light shadow-professional"
              >
                <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center shadow-professional">
                  <Bot className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <LoadingSpinner />
                    <span className="text-sm text-neutral-700 font-medium">Analyzing your request...</span>
                  </div>
                  <p className="text-xs text-neutral-500 mt-1">This may take a few moments</p>
                </div>
              </motion.div>
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center space-x-4 p-6 bg-red-50/80 backdrop-blur-sm border border-red-200/50 rounded-2xl shadow-professional"
              >
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-7 h-7 text-red-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-red-700 font-medium">{error}</p>
                  <button
                    onClick={handleRetry}
                    className="mt-2 text-xs text-red-600 hover:text-red-800 underline font-medium transition-colors"
                  >
                    Try again
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="gradient-card border-professional-light px-6 py-6 shadow-professional-lg">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              placeholder="Ask me about investments, retirement planning, or financial advice..."
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRetry}
              disabled={messages.length === 0 || isLoading}
              className="p-3 text-neutral-500 hover:text-neutral-700 hover:bg-white/60 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg border-professional-light"
              title="Retry last message"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            
            <button
              onClick={handleClearChat}
              disabled={messages.length === 0 || isLoading}
              className="p-3 text-neutral-500 hover:text-red-600 hover:bg-red-50/60 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg border-professional-light"
              title="Clear chat"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        {/* Tool Selector */}
        <div className="mt-4">
          <ToolSelector />
        </div>
      </div>
      
      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
};

export default ChatInterface; 