import { useState, useEffect } from 'react';

interface ApiKeys {
  openai: string;
  tavily: string;
  langsmith: string;
  cohere: string;
}

const CACHE_KEY = 'wealth-advisor-api-keys';

export const useApiKeys = () => {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: '',
    tavily: '',
    langsmith: '',
    cohere: '',
  });
  const [isLoaded, setIsLoaded] = useState(false);

  // Load cached keys on mount
  useEffect(() => {
    const loadCachedKeys = () => {
      try {
        const cached = localStorage.getItem(CACHE_KEY);
        if (cached) {
          const parsed = JSON.parse(cached);
          setApiKeys(parsed);
        }
      } catch (error) {
        console.error('Failed to load cached API keys:', error);
      } finally {
        setIsLoaded(true);
      }
    };

    loadCachedKeys();
  }, []);

  // Save keys to cache
  const saveKeys = (keys: ApiKeys) => {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(keys));
      setApiKeys(keys);
      return true;
    } catch (error) {
      console.error('Failed to save API keys:', error);
      return false;
    }
  };

  // Update a single key
  const updateKey = (key: keyof ApiKeys, value: string) => {
    const updatedKeys = { ...apiKeys, [key]: value };
    saveKeys(updatedKeys);
  };

  // Clear all cached keys
  const clearCache = () => {
    try {
      localStorage.removeItem(CACHE_KEY);
      setApiKeys({
        openai: '',
        tavily: '',
        langsmith: '',
        cohere: '',
      });
      return true;
    } catch (error) {
      console.error('Failed to clear API keys cache:', error);
      return false;
    }
  };

  // Check if any keys are cached
  const hasCachedKeys = () => {
    return Object.values(apiKeys).some(key => key.trim() !== '');
  };

  // Get keys for backend submission
  const getKeysForBackend = () => {
    return {
      openai: apiKeys.openai,
      tavily: apiKeys.tavily,
      langsmith: apiKeys.langsmith,
      cohere: apiKeys.cohere,
    };
  };

  return {
    apiKeys,
    isLoaded,
    saveKeys,
    updateKey,
    clearCache,
    hasCachedKeys,
    getKeysForBackend,
  };
}; 