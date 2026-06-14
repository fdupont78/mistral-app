/**
 * Conversation list component for the sidebar
 */

import React, { useState } from 'react';
import { Conversation } from '../types';

export interface ConversationListProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  onSelect: (conversation: Conversation) => void;
  onDelete: (id: number) => void;
  onUpdate: (id: number, title: string) => void;
}

export function ConversationList({
  conversations,
  currentConversation,
  onSelect,
  onDelete,
  onUpdate,
}: ConversationListProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState<string>('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  // Format date for display
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return date.toLocaleDateString('fr-FR', { weekday: 'short' });
      } else {
        return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
      }
    } catch {
      return dateString;
    }
  };

  // Handle edit start
  const handleEditStart = (conversation: Conversation) => {
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  // Handle edit save
  const handleEditSave = async (id: number) => {
    if (editTitle.trim()) {
      await onUpdate(id, editTitle.trim());
    }
    setEditingId(null);
    setEditTitle('');
  };

  // Handle edit cancel
  const handleEditCancel = () => {
    setEditingId(null);
    setEditTitle('');
  };

  // Handle delete confirmation
  const handleDeleteClick = (id: number) => {
    setConfirmDeleteId(id);
  };

  // Handle delete confirm
  const handleDeleteConfirm = async (id: number) => {
    await onDelete(id);
    setConfirmDeleteId(null);
  };

  // Handle delete cancel
  const handleDeleteCancel = () => {
    setConfirmDeleteId(null);
  };

  // Handle key down for edit input
  const handleEditKeyDown = (e: React.KeyboardEvent, id: number) => {
    if (e.key === 'Enter') {
      handleEditSave(id);
    } else if (e.key === 'Escape') {
      handleEditCancel();
    }
  };

  if (conversations.length === 0) {
    return (
      <div className="text-center text-gray-500 text-sm py-4">
        No conversations yet. Start a new one!
      </div>
    );
  }

  return (
    <div className="space-y-1 overflow-y-auto max-h-[400px]">
      {conversations.map((conversation) => (
        <div
          key={conversation.id}
          className={`p-2 rounded-lg cursor-pointer transition-colors ${
            currentConversation?.id === conversation.id
              ? 'bg-blue-100 hover:bg-blue-200'
              : 'hover:bg-gray-100'
          }`}
          onClick={() => onSelect(conversation)}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              {editingId === conversation.id ? (
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onKeyDown={(e) => handleEditKeyDown(e, conversation.id)}
                  onClick={(e) => e.stopPropagation()}
                  autoFocus
                  className="w-full px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              ) : (
                <div className="text-sm font-medium truncate">
                  {conversation.title}
                </div>
              )}
              <div className="text-xs text-gray-500">
                {formatDate(conversation.updated_at)}
              </div>
            </div>
            
            <div
              className="flex space-x-1 ml-2"
              onClick={(e) => e.stopPropagation()}
            >
              {editingId === conversation.id ? (
                <>
                  <button
                    onClick={() => handleEditSave(conversation.id)}
                    className="p-1 text-green-500 hover:bg-green-100 rounded"
                    title="Save"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </button>
                  <button
                    onClick={handleEditCancel}
                    className="p-1 text-gray-500 hover:bg-gray-100 rounded"
                    title="Cancel"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="15" y1="9" x2="9" y2="15"></line>
                      <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => handleEditStart(conversation)}
                    className="p-1 text-gray-500 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100"
                    title="Edit"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDeleteClick(conversation.id)}
                    className="p-1 text-red-500 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      ))}

      {/* Delete confirmation modal */}
      {confirmDeleteId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Delete Conversation</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this conversation? This action cannot be undone.
            </p>
            <div className="flex space-x-3 justify-end">
              <button
                onClick={handleDeleteCancel}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteConfirm(confirmDeleteId)}
                className="px-4 py-2 bg-red-500 text-white hover:bg-red-600 rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConversationList;
