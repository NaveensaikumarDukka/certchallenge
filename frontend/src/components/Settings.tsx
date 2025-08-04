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
  RefreshCw,
  Trash2
} from 'lucide-react';
import { testBackendConnection } from '@/lib/api';
import { useApiKeys } from '@/hooks/useApiKeys';

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
  const {
    apiKeys,
    isLoaded,
    saveKeys,
    updateKey,
    clearCache,
    hasCachedKeys,
    getKeysForBackend,
  } = useApiKeys();
  
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
  const [configuredKeys, setConfiguredKeys] = useState<string[]>([]);

  // Check backend connection and configured keys on mount
  useEffect(() => {
    checkBackendConnection();
    checkConfiguredKeys();
  }, []);

  const checkConfiguredKeys = async () => {
    try {
      const response = await fetch('/api/settings/status');
      if (response.ok) {
        const data = await response.json();
        const configured = [];
        if (data.openai_configured) configured.push('OpenAI');
        if (data.tavily_configured) configured.push('Tavily');
        if (data.cohere_configured) configured.push('Cohere');
        if (data.langsmith_configured) configured.push('LangSmith');
        setConfiguredKeys(configured);
      }
    } catch (error) {
      console.error('Failed to check configured keys:', error);
    }
  };

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
    updateKey(key, value);
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
      // Get only non-empty keys
      const keysToSend = getKeysForBackend();
      const nonEmptyKeys = Object.entries(keysToSend).filter(([_, value]) => value.trim() !== '');
      
      if (nonEmptyKeys.length === 0) {
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
        return;
      }

      // Send only non-empty keys to backend
      const keysToSendFiltered = Object.fromEntries(nonEmptyKeys);
      console.log('Sending API keys to backend:', keysToSendFiltered);
      
      const response = await fetch('/api/settings/save-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(keysToSendFiltered),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Backend response:', result);

      setSaveStatus('success');
      // Refresh configured keys status
      await checkConfiguredKeys();
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

  const handleClearCache = () => {
    clearCache();
    setSaveStatus('success');
    setTimeout(() => setSaveStatus('idle'), 2000);
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
              {/* Cache Status */}
              {!isLoaded ? (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />
                    <span className="text-sm font-medium text-blue-800">
                      Loading cached API keys...
                    </span>
                  </div>
                </div>
              ) : hasCachedKeys() ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium text-green-800">
                      API keys are cached locally. They will be automatically loaded on app startup.
                    </span>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    <span className="text-sm font-medium text-yellow-800">
                      No API keys cached. Enter your keys below and they will be saved automatically.
                    </span>
                  </div>
                </div>
              )}
              
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

              {/* Configured Keys Status */}
              {configuredKeys.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium text-green-800">
                      Configured in Backend:
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {configuredKeys.map((key) => (
                      <span
                        key={key}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                      >
                        {key}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* API Keys Section */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">API Keys</h3>
                <div className="space-y-4">
                  {/* OpenAI */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
                      <span>OpenAI API Key</span>
                      {apiKeys.openai && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                          Cached
                        </span>
                      )}
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.openai ? 'text' : 'password'}
                        value={apiKeys.openai}
                        onChange={(e) => handleInputChange('openai', e.target.value)}
                        placeholder="sk-..."
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          apiKeys.openai ? 'border-green-300 bg-green-50/30' : 'border-gray-300'
                        }`}
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
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
                      <span>Tavily API Key</span>
                      {apiKeys.tavily && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                          Cached
                        </span>
                      )}
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.tavily ? 'text' : 'password'}
                        value={apiKeys.tavily}
                        onChange={(e) => handleInputChange('tavily', e.target.value)}
                        placeholder="tvly-..."
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          apiKeys.tavily ? 'border-green-300 bg-green-50/30' : 'border-gray-300'
                        }`}
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
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
                      <span>LangSmith API Key</span>
                      {apiKeys.langsmith && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                          Cached
                        </span>
                      )}
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.langsmith ? 'text' : 'password'}
                        value={apiKeys.langsmith}
                        onChange={(e) => handleInputChange('langsmith', e.target.value)}
                        placeholder="ls_..."
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          apiKeys.langsmith ? 'border-green-300 bg-green-50/30' : 'border-gray-300'
                        }`}
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
                    <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center justify-between">
                      <span>Cohere API Key</span>
                      {apiKeys.cohere && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                          Cached
                        </span>
                      )}
                    </label>
                    <div className="relative">
                      <input
                        type={showPasswords.cohere ? 'text' : 'password'}
                        value={apiKeys.cohere}
                        onChange={(e) => handleInputChange('cohere', e.target.value)}
                        placeholder="..."
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          apiKeys.cohere ? 'border-green-300 bg-green-50/30' : 'border-gray-300'
                        }`}
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
            <div className="flex items-center justify-between p-6 border-t border-gray-200">
              <div className="flex items-center space-x-3">
                {hasCachedKeys() && (
                  <button
                    onClick={handleClearCache}
                    className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
                    title="Clear cached API keys"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Clear Cache</span>
                  </button>
                )}
              </div>
              
              <div className="flex items-center space-x-3">
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
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SettingsModal; 