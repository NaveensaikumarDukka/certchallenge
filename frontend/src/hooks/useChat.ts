import { useState, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import type { Message, ChatState, AdvisorQueryRequest } from '@/lib/types';
import { queryAdvisor, handleAPIError } from '@/lib/api';

interface UseChatReturn extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  retryLastMessage: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toolsUsed, setToolsUsed] = useState<string[]>([]);
  const [confidence, setConfidence] = useState(0);
  
  const lastMessageRef = useRef<Message | null>(null);

  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const updateLastMessage = useCallback((updates: Partial<Message>) => {
    setMessages(prev => {
      if (prev.length === 0) return prev;
      const newMessages = [...prev];
      newMessages[newMessages.length - 1] = {
        ...newMessages[newMessages.length - 1],
        ...updates,
      };
      return newMessages;
    });
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    // Clear any previous errors
    setError(null);

    // Create user message
    const userMessage: Message = {
      id: uuidv4(),
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    addMessage(userMessage);

    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: uuidv4(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isStreaming: true,
    };

    addMessage(assistantMessage);
    setIsLoading(true);

    try {
      const request: AdvisorQueryRequest = {
        question: content.trim(),
        include_context: true,
        stream_response: false,
      };

      const response = await queryAdvisor(request);

      // Update assistant message with response
      updateLastMessage({
        content: response.response,
        tools_used: response.tools_used,
        confidence: response.confidence,
        context: response.context,
        isStreaming: false,
      });

      // Update global state
      setToolsUsed(response.tools_used);
      setConfidence(response.confidence);

      // Store last message for retry functionality
      lastMessageRef.current = userMessage;

    } catch (err) {
      const apiError = handleAPIError(err);
      setError(apiError.message);
      
      // Update assistant message with error
      updateLastMessage({
        content: `Sorry, I encountered an error: ${apiError.message}`,
        isStreaming: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, updateLastMessage]);

  const retryLastMessage = useCallback(async () => {
    if (!lastMessageRef.current) return;
    
    // Remove the last assistant message
    setMessages(prev => prev.slice(0, -1));
    
    // Retry the last user message
    await sendMessage(lastMessageRef.current.content);
  }, [sendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setToolsUsed([]);
    setConfidence(0);
    lastMessageRef.current = null;
  }, []);

  return {
    messages,
    isLoading,
    error,
    tools_used: toolsUsed,
    confidence,
    sendMessage,
    clearMessages,
    retryLastMessage,
  };
}; 