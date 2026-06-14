/**
 * Main chat interface component
 */

import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Message, GenerationParams } from '../types';
import MessageBubble from './MessageBubble';

export interface ChatInterfaceProps {
  messages: Message[];
  currentConversation: { id: number; title: string } | null;
  isGenerating: boolean;
  modelReady: boolean;
  generationParams: GenerationParams;
  onSend: (content: string) => Promise<void>;
  onUpdateTitle: (title: string) => void;
}

export function ChatInterface({
  messages,
  currentConversation,
  isGenerating,
  modelReady,
  generationParams,
  onSend,
  onUpdateTitle,
}: ChatInterfaceProps) {
  const [input, setInput] = useState<string>('');
  const [isComposing, setIsComposing] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
  };

  // Handle form submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !modelReady || isGenerating) return;

    const content = input.trim();
    setInput('');
    await onSend(content);
  };

  // Handle key down for textarea
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  // Handle composition events for IME
  const handleCompositionStart = () => setIsComposing(true);
  const handleCompositionEnd = () => setIsComposing(false);

  // Handle title change
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (currentConversation) {
      onUpdateTitle(e.target.value);
    }
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return timestamp;
    }
  };

  // Check if we should show the empty state
  const showEmptyState = messages.length === 0 && !isGenerating;

  return (
    <div className="flex-1 flex flex-col h-full bg-gray-50">
      {/* Conversation header */}
      {currentConversation && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <input
            type="text"
            value={currentConversation.title}
            onChange={handleTitleChange}
            className="w-full text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 bg-transparent"
            placeholder="Conversation title"
          />
          <div className="text-xs text-gray-500 mt-1">
            Updated: {formatTimestamp(currentConversation.updated_at)}
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {showEmptyState ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="mb-4 opacity-50">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p className="text-center">Start the conversation by sending a message below.</p>
            {!modelReady && (
              <p className="text-sm text-gray-400 mt-2">
                Please load the model first using the sidebar.
              </p>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}

        {/* Generating indicator */}
        {isGenerating && (
          <div className="flex justify-start">
            <div className="bg-gray-200 rounded-lg px-4 py-3 max-w-[80%]">
              <div className="flex items-center">
                <div className="flex space-x-1 mr-3">
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <span className="text-gray-600 text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex flex-col">
          <div className="flex items-end border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
            <textarea
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onCompositionStart={handleCompositionStart}
              onCompositionEnd={handleCompositionEnd}
              placeholder={modelReady ? "Type your message here... (Shift+Enter for new line)" : "Please load the model first"}
              disabled={!modelReady || isGenerating}
              rows={1}
              className="flex-1 p-3 resize-none focus:outline-none bg-transparent disabled:opacity-50"
              style={{ maxHeight: '150px' }}
            />
            <button
              type="submit"
              disabled={!input.trim() || !modelReady || isGenerating}
              className="p-3 text-blue-500 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed rounded-r-lg"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
          
          {/* Generation params summary */}
          <div className="text-xs text-gray-400 mt-2 flex flex-wrap gap-2">
            <span>Temp: {generationParams.temperature.toFixed(2)}</span>
            <span>Top P: {generationParams.top_p.toFixed(2)}</span>
            <span>Top K: {generationParams.top_k}</span>
            <span>Max Tokens: {generationParams.max_new_tokens}</span>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ChatInterface;
