'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Key, 
  Save, 
  Eye, 
  EyeOff, 
  CheckCircle, 
  AlertCircle, 
  TestTube,
  RefreshCw
} from 'lucide-react';
import { testBackendConnection } from '@/lib/api';

interface ApiKeys {
  openai: string;
  tavily: string;
  langsmith: string;
  cohere: string;
}

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsModal: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: '',
    tavily: '',
    langsmith: '',
    cohere: '',
  });
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({
    openai: false,
    tavily: false,
    langsmith: false,
    cohere: false,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [testStatus, setTestStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // Load saved API keys on component mount
  useEffect(() => {
    const savedKeys = localStorage.getItem('wealth-advisor-api-keys');
    if (savedKeys) {
      try {
        const parsed = JSON.parse(savedKeys);
        setApiKeys(parsed);
      } catch (error) {
        console.error('Failed to parse saved API keys:', error);
      }
    }
  }, []);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    setBackendStatus('checking');
    try {
      const isConnected = await testBackendConnection();
      setBackendStatus(isConnected ? 'connected' : 'disconnected');
    } catch (error) {
      setBackendStatus('disconnected');
    }
  };

  const handleInputChange = (key: keyof ApiKeys, value: string) => {
    setApiKeys((prev: ApiKeys) => ({
      ...prev,
      [key]: value,
    }));
  };

  const togglePasswordVisibility = (key: string) => {
    setShowPasswords((prev: Record<string, boolean>) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus('idle');

    try {
      // Validate that at least one API key is provided
      const hasAnyKey = Object.values(apiKeys).some((key: string) => key.trim() !== '');
      if (!hasAnyKey) {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
        return;
      }

      // Save to localStorage
      localStorage.setItem('wealth-advisor-api-keys', JSON.stringify(apiKeys));
      
      // Send to backend
      await fetch('/api/settings/save-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiKeys),
      });

      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to save API keys:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestStatus('idle');

    try {
      const isConnected = await testBackendConnection();
      setTestStatus(isConnected ? 'success' : 'error');
      setBackendStatus(isConnected ? 'connected' : 'disconnected');
    } catch (error) {
      setTestStatus('error');
      setBackendStatus('disconnected');
    } finally {
      setIsTesting(false);
      setTimeout(() => setTestStatus('idle'), 3000);
    }
  };

  const getStatusIcon = (status: 'connected' | 'disconnected' | 'checking') => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'disconnected':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'checking':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
    }
  };

  const getStatusText = (status: 'connected' | 'disconnected' | 'checking') => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'disconnected':
        return 'Disconnected';
      case 'checking':
        return 'Checking...';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <SettingsIcon className="w-6 h-6 text-gray-600" />
                <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Backend Status */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Backend Status:</span>
                    {getStatusIcon(backendStatus)}
                    <span className={`text-sm ${
                      backendStatus === 'connected' ? 'text-green-600' : 
                      backendStatus === 'disconnected' ? 'text-red-600' : 
                      'text-blue-600'
                    }`}>
                      {getStatusText(backendStatus)}
                    </span>
                  </div>
                  <button
                    onClick={handleTestConnection}
                    disabled={isTesting}
                    className="flex items-center space-x-1 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 disabled:opacity-50 transition-colors"
                  >
                    <TestTube className="w-3 h-3" />
                    <span>Test</span>
                  </button>
                </div>
              </div>

              {/* API Keys Section */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">API Keys</h3>
                <div className="space-y-4">
                  {/* OpenAI */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      OpenAI API Key
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.openai ? 'text' : 'password'}
                        value={apiKeys.openai}
                        onChange={(e) => handleInputChange('openai', e.target.value)}
                        placeholder="sk-..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('openai')}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.openai ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Tavily */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Tavily API Key
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.tavily ? 'text' : 'password'}
                        value={apiKeys.tavily}
                        onChange={(e) => handleInputChange('tavily', e.target.value)}
                        placeholder="tvly-..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('tavily')}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.tavily ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* LangSmith */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      LangSmith API Key
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.langsmith ? 'text' : 'password'}
                        value={apiKeys.langsmith}
                        onChange={(e) => handleInputChange('langsmith', e.target.value)}
                        placeholder="ls_..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('langsmith')}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.langsmith ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Cohere */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cohere API Key
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.cohere ? 'text' : 'password'}
                        value={apiKeys.cohere}
                        onChange={(e) => handleInputChange('cohere', e.target.value)}
                        placeholder="..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility('cohere')}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPasswords.cohere ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Save Status */}
              <AnimatePresence>
                {saveStatus !== 'idle' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex items-center space-x-2 p-3 rounded-md ${
                      saveStatus === 'success' 
                        ? 'bg-green-50 text-green-700 border border-green-200' 
                        : 'bg-red-50 text-red-700 border border-red-200'
                    }`}
                  >
                    {saveStatus === 'success' ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <AlertCircle className="w-4 h-4" />
                    )}
                    <span className="text-sm">
                      {saveStatus === 'success' 
                        ? 'API keys saved successfully!' 
                        : 'Failed to save API keys. Please try again.'
                      }
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Test Status */}
              <AnimatePresence>
                {testStatus !== 'idle' && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex items-center space-x-2 p-3 rounded-md ${
                      testStatus === 'success' 
                        ? 'bg-green-50 text-green-700 border border-green-200' 
                        : 'bg-red-50 text-red-700 border border-red-200'
                    }`}
                  >
                    {testStatus === 'success' ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <AlertCircle className="w-4 h-4" />
                    )}
                    <span className="text-sm">
                      {testStatus === 'success' 
                        ? 'Backend connection successful!' 
                        : 'Backend connection failed. Please check your setup.'
                      }
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSaving ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{isSaving ? 'Saving...' : 'Save'}</span>
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SettingsModal; 