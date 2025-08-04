'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User, ExternalLink, Copy, Check, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message as MessageType } from '@/lib/types';

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  };

  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`flex items-start space-x-4 max-w-4xl ${
          isUser ? 'flex-row-reverse space-x-reverse' : ''
        }`}
      >
        {/* Avatar */}
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 shadow-professional ${
            isUser
              ? 'gradient-primary'
              : 'bg-gradient-to-r from-emerald-500 to-teal-500'
          }`}
        >
          {isUser ? (
            <User className="w-6 h-6 text-white" />
          ) : (
            <Sparkles className="w-6 h-6 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div
          className={`flex-1 ${
            isUser ? 'text-right' : 'text-left'
          }`}
        >
          <div
            className={`inline-block p-6 rounded-2xl max-w-full shadow-professional ${
              isUser
                ? 'gradient-primary text-white'
                : 'gradient-card border-professional-light text-neutral-900'
            }`}
          >
            {message.isStreaming ? (
              <div className="flex items-center space-x-3">
                <div className="loading-dots">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>
                <span className="text-sm font-medium">Typing...</span>
              </div>
            ) : (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  className={`markdown ${
                    isUser ? 'text-white' : 'text-neutral-900'
                  }`}
                  components={{
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`inline-flex items-center space-x-1 transition-colors ${
                          isUser
                            ? 'text-blue-100 hover:text-white'
                            : 'text-blue-600 hover:text-blue-800'
                        }`}
                      >
                        <span>{children}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ),
                    code: ({ children }) => (
                      <code
                        className={`px-2 py-1 rounded-md text-xs font-mono ${
                          isUser
                            ? 'bg-white/20 text-white border border-white/30'
                            : 'bg-neutral-100 text-neutral-800 border border-neutral-200'
                        }`}
                      >
                        {children}
                      </code>
                    ),
                    pre: ({ children }) => (
                      <pre
                        className={`p-4 rounded-lg overflow-x-auto text-xs border ${
                          isUser
                            ? 'bg-white/20 text-white border-white/30'
                            : 'bg-neutral-50 text-neutral-800 border-neutral-200'
                        }`}
                      >
                        {children}
                      </pre>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* Message Metadata */}
          <div
            className={`flex items-center space-x-3 mt-3 text-xs text-neutral-500 ${
              isUser ? 'justify-end' : 'justify-start'
            }`}
          >
            <span className="font-medium">
              {message.timestamp.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>

            {/* Tools Used */}
            {message.tools_used && message.tools_used.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="font-medium">Tools:</span>
                <div className="flex items-center space-x-1">
                  {message.tools_used.map((tool) => (
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

            {/* Confidence Score */}
            {message.confidence && message.confidence > 0 && (
              <div className="flex items-center space-x-1 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-200">
                <span className="font-medium text-emerald-700">
                  {Math.round(message.confidence * 100)}% confidence
                </span>
              </div>
            )}

            {/* Copy Button */}
            {!isUser && (
              <button
                onClick={handleCopy}
                className="p-1.5 hover:bg-neutral-100 rounded-lg transition-all duration-200 border border-transparent hover:border-neutral-200"
                title="Copy message"
              >
                {copied ? (
                  <Check className="w-3 h-3 text-emerald-600" />
                ) : (
                  <Copy className="w-3 h-3 text-neutral-500" />
                )}
              </button>
            )}
          </div>


        </div>
      </div>
    </motion.div>
  );
};

export default Message; 