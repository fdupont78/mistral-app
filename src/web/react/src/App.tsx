/**
 * Main App component for Mistral Chat React frontend
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useConversations, useModel, useGeneration } from './hooks';
import { Sidebar, ChatInterface } from './components';
import { GenerationParams, DEFAULT_GENERATION_PARAMS, QuantizationMethod } from './types';
import { chatApi } from './api/client';

function App() {
  // State from custom hooks
  const {
    conversations,
    currentConversation,
    messages,
    isLoading: isLoadingConversations,
    error: conversationsError,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
    addMessage,
  } = useConversations();

  const {
    status: modelStatus,
    quantizationMethod,
    autoLoadModel,
    isLoading: isLoadingModel,
    error: modelError,
    loadModel,
    unloadModel,
    setQuantizationMethod,
    setAutoLoadModel,
    checkStatus,
  } = useModel();

  const {
    params: generationParams,
    isGenerating,
    error: generationError,
    setParams,
    generateResponse,
  } = useGeneration();

  // Local state
  const [error, setError] = useState<string | null>(null);

  // Check for dry-run mode
  const isDryRunMode = import.meta.env.VITE_DRY_RUN === 'true';

  // Check if model is ready (loaded or dry-run mode)
  const modelReady = modelStatus.loaded || isDryRunMode;

  // Load model on mount if auto-load is enabled
  useEffect(() => {
    if (autoLoadModel && !modelStatus.loaded && !modelStatus.loading && !isDryRunMode) {
      loadModel(quantizationMethod);
    }
  }, [autoLoadModel, modelStatus.loaded, modelStatus.loading, isDryRunMode, quantizationMethod, loadModel]);

  // Handle sending a message
  const handleSend = useCallback(async (content: string) => {
    if (!currentConversation || isGenerating) return;

    try {
      // Add user message
      await addMessage(currentConversation.id, 'user', content);

      // Generate response
      await generateResponse(currentConversation.id, isDryRunMode);

      // Reload messages to get the assistant response
      // Note: The generateResponse function already saves the assistant response
      // but we need to reload to show it in the UI
      // This is handled by the useConversations hook
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
    }
  }, [currentConversation, isGenerating, addMessage, generateResponse, isDryRunMode]);

  // Handle new conversation
  const handleNewConversation = useCallback(async () => {
    try {
      await createConversation('New Chat');
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError('Failed to create conversation');
    }
  }, [createConversation]);

  // Handle conversation selection
  const handleSelectConversation = useCallback(async (conversation: any) => {
    try {
      await selectConversation(conversation);
    } catch (err) {
      console.error('Failed to select conversation:', err);
      setError('Failed to select conversation');
    }
  }, [selectConversation]);

  // Handle conversation deletion
  const handleDeleteConversation = useCallback(async (id: number) => {
    try {
      await deleteConversation(id);
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
    }
  }, [deleteConversation]);

  // Handle conversation title update
  const handleUpdateConversationTitle = useCallback(async (id: number, title: string) => {
    try {
      await updateConversationTitle(id, title);
    } catch (err) {
      console.error('Failed to update conversation title:', err);
      setError('Failed to update conversation title');
    }
  }, [updateConversationTitle]);

  // Handle model load
  const handleLoadModel = useCallback(async (quantMethod: QuantizationMethod) => {
    try {
      setQuantizationMethod(quantMethod);
      await loadModel(quantMethod);
    } catch (err) {
      console.error('Failed to load model:', err);
      setError('Failed to load model');
    }
  }, [loadModel, setQuantizationMethod]);

  // Handle model unload
  const handleUnloadModel = useCallback(async () => {
    try {
      await unloadModel();
    } catch (err) {
      console.error('Failed to unload model:', err);
      setError('Failed to unload model');
    }
  }, [unloadModel]);

  // Handle auto-load toggle
  const handleToggleAutoLoad = useCallback((value: boolean) => {
    setAutoLoadModel(value);
  }, [setAutoLoadModel]);

  // Handle generation params change
  const handleGenerationParamsChange = useCallback((params: GenerationParams) => {
    setParams(params);
  }, [setParams]);

  // Handle title update for current conversation
  const handleUpdateTitle = useCallback((title: string) => {
    if (currentConversation) {
      handleUpdateConversationTitle(currentConversation.id, title);
    }
  }, [currentConversation, handleUpdateConversationTitle]);

  // Show loading state
  if (isLoadingConversations || isLoadingModel) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (conversationsError || modelError || generationError || error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md">
          <h2 className="text-xl font-semibold text-red-500 mb-4">Error</h2>
          <p className="text-gray-600 mb-4">
            {conversationsError || modelError || generationError || error}
          </p>
          <button
            onClick={() => {
              setError(null);
              checkStatus();
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        currentConversation={currentConversation}
        modelStatus={modelStatus}
        quantizationMethod={quantizationMethod}
        autoLoadModel={autoLoadModel}
        generationParams={generationParams}
        onNewConversation={handleNewConversation}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onUpdateConversation={handleUpdateConversationTitle}
        onLoadModel={handleLoadModel}
        onUnloadModel={handleUnloadModel}
        onToggleAutoLoad={handleToggleAutoLoad}
        onGenerationParamsChange={handleGenerationParamsChange}
      />

      {/* Main chat area */}
      <ChatInterface
        messages={messages}
        currentConversation={currentConversation}
        isGenerating={isGenerating}
        modelReady={modelReady}
        generationParams={generationParams}
        onSend={handleSend}
        onUpdateTitle={handleUpdateTitle}
      />
    </div>
  );
}

export default App;
