/**
 * Custom hook for managing generation parameters and generating responses
 */

import { useState, useCallback } from 'react';
import { GenerationParams, DEFAULT_GENERATION_PARAMS } from '../types';
import { chatApi } from '../api/client';

export interface UseGenerationReturn {
  params: GenerationParams;
  isGenerating: boolean;
  error: string | null;
  setParams: (params: Partial<GenerationParams>) => void;
  resetParams: () => void;
  generateResponse: (
    convId: number,
    dryRun?: boolean
  ) => Promise<string | null>;
}

export function useGeneration(): UseGenerationReturn {
  const [params, setParams] = useState<GenerationParams>(DEFAULT_GENERATION_PARAMS);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Update generation parameters
  const updateParams = useCallback((newParams: Partial<GenerationParams>) => {
    setParams(prev => ({ ...prev, ...newParams }));
  }, []);

  // Reset to default parameters
  const resetParams = useCallback(() => {
    setParams(DEFAULT_GENERATION_PARAMS);
  }, []);

  // Generate a response
  const generateResponse = useCallback(async (
    convId: number,
    dryRun: boolean = false
  ): Promise<string | null> => {
    try {
      setIsGenerating(true);
      setError(null);
      
      const response = await chatApi.generation.generate(convId, {
        params,
        dry_run: dryRun,
      });
      
      return response.response;
    } catch (err) {
      console.error('Failed to generate response:', err);
      setError('Failed to generate response');
      return null;
    } finally {
      setIsGenerating(false);
    }
  }, [params]);

  return {
    params,
    isGenerating,
    error,
    setParams: updateParams,
    resetParams,
    generateResponse,
  };
}

export default useGeneration;
