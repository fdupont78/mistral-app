/**
 * Custom hook for managing model state
 */

import { useState, useCallback, useEffect } from 'react';
import { ModelStatus, QuantizationMethod, QUANTIZATION_OPTIONS } from '../types';
import { chatApi } from '../api/client';

export interface UseModelReturn {
  status: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  isLoading: boolean;
  error: string | null;
  loadModel: (quantMethod?: QuantizationMethod) => Promise<boolean>;
  unloadModel: () => Promise<boolean>;
  setQuantizationMethod: (method: QuantizationMethod) => void;
  setAutoLoadModel: (value: boolean) => void;
  checkStatus: () => Promise<void>;
}

export function useModel(): UseModelReturn {
  const [status, setStatus] = useState<ModelStatus>({
    loaded: false,
    loading: false,
    status: 'Not loaded',
  });
  const [quantizationMethod, setQuantizationMethod] = useState<QuantizationMethod>('fp8');
  const [autoLoadModel, setAutoLoadModel] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Check model status
  const checkStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await chatApi.model.getStatus();
      setStatus(data);
    } catch (err) {
      console.error('Failed to check model status:', err);
      setError('Failed to check model status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load model
  const loadModel = useCallback(async (quantMethod: QuantizationMethod = quantizationMethod): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Update quantization method if provided
      if (quantMethod !== quantizationMethod) {
        setQuantizationMethod(quantMethod);
      }
      
      await chatApi.model.load(quantMethod);
      
      // Poll for status until loaded or error
      const pollStatus = async () => {
        const data = await chatApi.model.getStatus();
        setStatus(data);
        
        if (data.loading) {
          // Still loading, check again in 1 second
          setTimeout(pollStatus, 1000);
        }
      };
      
      // Start polling
      await pollStatus();
      
      return true;
    } catch (err) {
      console.error('Failed to load model:', err);
      setError('Failed to load model');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [quantizationMethod]);

  // Unload model
  const unloadModel = useCallback(async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await chatApi.model.unload();
      await checkStatus();
      return true;
    } catch (err) {
      console.error('Failed to unload model:', err);
      setError('Failed to unload model');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [checkStatus]);

  // Get quantization options
  const getQuantizationOptions = useCallback(() => {
    return QUANTIZATION_OPTIONS;
  }, []);

  // Initial status check
  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return {
    status,
    quantizationMethod,
    autoLoadModel,
    isLoading,
    error,
    loadModel,
    unloadModel,
    setQuantizationMethod,
    setAutoLoadModel,
    checkStatus,
  };
}

export default useModel;
