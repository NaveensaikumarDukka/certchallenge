'use client';

import React, { useState, useEffect } from 'react';
import { Search, FileText, TrendingUp, Database, Settings, Wifi, WifiOff } from 'lucide-react';
import { getBackendStatus } from '@/lib/api';
import type { SystemStatus } from '@/lib/types';

interface Tool {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  enabled: boolean;
}

const ToolSelector: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await getBackendStatus();
        setSystemStatus(status);
      } catch (error) {
        console.error('Failed to get system status:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const tools: Tool[] = [
    {
      id: 'tavily',
      name: 'Tavily Search',
      description: 'Web search for latest information',
      icon: Search,
      color: 'bg-blue-50 text-blue-700 border-blue-200',
      enabled: systemStatus?.services?.tavily_search || false,
    },
    {
      id: 'arxiv',
      name: 'ArXiv Papers',
      description: 'Academic research papers',
      icon: FileText,
      color: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      enabled: systemStatus?.services?.arxiv_search || false,
    },
    {
      id: 'yfinance',
      name: 'Yahoo Finance',
      description: 'Real-time stock data',
      icon: TrendingUp,
      color: 'bg-amber-50 text-amber-700 border-amber-200',
      enabled: systemStatus?.services?.yfinance_data || false,
    },
    {
      id: 'rag',
      name: 'RAG System',
      description: 'Document knowledge base',
      icon: Database,
      color: 'bg-purple-50 text-purple-700 border-purple-200',
      enabled: systemStatus?.services?.rag_service || false,
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-3">
        <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        <span className="ml-2 text-xs text-neutral-500 font-medium">Checking available tools...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between bg-white/60 backdrop-blur-sm px-4 py-3 rounded-xl border border-neutral-200/50">
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 text-xs text-neutral-600 font-medium">
          <Settings className="w-4 h-4" />
          <span>Available Tools:</span>
        </div>
        
        <div className="flex items-center space-x-2">
          {tools.map((tool) => (
            <div
              key={tool.id}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 border ${
                tool.enabled
                  ? `${tool.color} shadow-sm`
                  : 'bg-neutral-100 text-neutral-400 border-neutral-200'
              }`}
              title={`${tool.name}: ${tool.description}`}
            >
              <tool.icon className="w-3 h-3" />
              <span className="hidden sm:inline">{tool.name}</span>
            </div>
          ))}
        </div>
      </div>
      
      {systemStatus && (
        <div className="flex items-center space-x-2 text-xs">
          <div className="flex items-center space-x-1 px-2 py-1 rounded-full bg-neutral-50 border border-neutral-200">
            {systemStatus.status === 'healthy' ? (
              <Wifi className="w-3 h-3 text-emerald-600" />
            ) : (
              <WifiOff className="w-3 h-3 text-red-500" />
            )}
            <span className={`font-medium ${
              systemStatus.status === 'healthy' ? 'text-emerald-700' : 'text-red-600'
            }`}>
              {systemStatus.status === 'healthy' ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolSelector; 