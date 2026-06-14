/**
 * Sidebar component containing model controls, conversations, and generation parameters
 */

import React from 'react';
import { Conversation, ModelStatus, QuantizationMethod, GenerationParams } from '../types';
import ModelControls from './ModelControls';
import ConversationList from './ConversationList';
import GenerationParamsComponent from './GenerationParams';

export interface SidebarProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  modelStatus: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  generationParams: GenerationParams;
  onNewConversation: () => void;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (id: number) => void;
  onUpdateConversation: (id: number, title: string) => void;
  onLoadModel: (quantMethod: QuantizationMethod) => void;
  onUnloadModel: () => void;
  onToggleAutoLoad: (value: boolean) => void;
  onGenerationParamsChange: (params: GenerationParams) => void;
}

export function Sidebar({
  conversations,
  currentConversation,
  modelStatus,
  quantizationMethod,
  autoLoadModel,
  generationParams,
  onNewConversation,
  onSelectConversation,
  onDeleteConversation,
  onUpdateConversation,
  onLoadModel,
  onUnloadModel,
  onToggleAutoLoad,
  onGenerationParamsChange,
}: SidebarProps) {
  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col h-full">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-800 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          Mistral Chat
        </h1>
      </div>

      {/* New conversation button */}
      <button
        onClick={onNewConversation}
        className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors mb-6 flex items-center justify-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Chat
      </button>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        {/* Model Controls */}
        <ModelControls
          status={modelStatus}
          quantizationMethod={quantizationMethod}
          autoLoadModel={autoLoadModel}
          onLoad={onLoadModel}
          onUnload={onUnloadModel}
          onToggleAutoLoad={onToggleAutoLoad}
        />

        {/* Conversations */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            Conversations
          </h2>
          <ConversationList
            conversations={conversations}
            currentConversation={currentConversation}
            onSelect={onSelectConversation}
            onDelete={onDeleteConversation}
            onUpdate={onUpdateConversation}
          />
        </div>

        {/* Generation Parameters */}
        <GenerationParamsComponent
          params={generationParams}
          onChange={onGenerationParamsChange}
        />
      </div>
    </div>
  );
}

export default Sidebar;
