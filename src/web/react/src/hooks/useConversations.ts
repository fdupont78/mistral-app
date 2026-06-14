/**
 * Custom hook for managing conversations
 */

import { useState, useCallback, useEffect } from 'react';
import { Conversation, Message } from '../types';
import { chatApi } from '../api/client';

export interface UseConversationsReturn {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  loadConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<Conversation | null>;
  selectConversation: (conversation: Conversation) => Promise<void>;
  deleteConversation: (id: number) => Promise<boolean>;
  updateConversationTitle: (id: number, title: string) => Promise<boolean>;
  loadMessages: (convId: number) => Promise<void>;
  addMessage: (convId: number, role: 'user' | 'assistant', content: string) => Promise<number | null>;
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load all conversations
  const loadConversations = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await chatApi.conversations.list();
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
      setError('Failed to load conversations');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Create a new conversation
  const createConversation = useCallback(async (title: string = 'New Chat'): Promise<Conversation | null> => {
    try {
      setError(null);
      const { id } = await chatApi.conversations.create({ title });
      await loadConversations();
      
      // Find and select the new conversation
      const newConversation = conversations.find(c => c.id === id);
      if (newConversation) {
        await selectConversation(newConversation);
        return newConversation;
      }
      return null;
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError('Failed to create conversation');
      return null;
    }
  }, [conversations, loadConversations]);

  // Select a conversation
  const selectConversation = useCallback(async (conversation: Conversation) => {
    try {
      setError(null);
      setCurrentConversation(conversation);
      await loadMessages(conversation.id);
    } catch (err) {
      console.error('Failed to select conversation:', err);
      setError('Failed to select conversation');
    }
  }, []);

  // Load messages for a conversation
  const loadMessages = useCallback(async (convId: number) => {
    try {
      setError(null);
      const data = await chatApi.messages.list(convId);
      setMessages(data);
    } catch (err) {
      console.error('Failed to load messages:', err);
      setError('Failed to load messages');
    }
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback(async (id: number): Promise<boolean> => {
    try {
      setError(null);
      await chatApi.conversations.delete(id);
      await loadConversations();
      
      // Clear current conversation if it was deleted
      if (currentConversation?.id === id) {
        setCurrentConversation(null);
        setMessages([]);
      }
      return true;
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      setError('Failed to delete conversation');
      return false;
    }
  }, [currentConversation, loadConversations]);

  // Update conversation title
  const updateConversationTitle = useCallback(async (id: number, title: string): Promise<boolean> => {
    try {
      setError(null);
      await chatApi.conversations.update(id, { title });
      await loadConversations();
      
      // Update current conversation if it was updated
      if (currentConversation?.id === id) {
        setCurrentConversation(prev => prev ? { ...prev, title } : null);
      }
      return true;
    } catch (err) {
      console.error('Failed to update conversation title:', err);
      setError('Failed to update conversation title');
      return false;
    }
  }, [currentConversation, loadConversations]);

  // Add a message to a conversation
  const addMessage = useCallback(async (convId: number, role: 'user' | 'assistant', content: string): Promise<number | null> => {
    try {
      setError(null);
      const { id } = await chatApi.messages.create(convId, { role, content });
      await loadMessages(convId);
      return id;
    } catch (err) {
      console.error('Failed to add message:', err);
      setError('Failed to add message');
      return null;
    }
  }, [loadMessages]);

  // Initial load
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return {
    conversations,
    currentConversation,
    messages,
    isLoading,
    error,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
    updateConversationTitle,
    loadMessages,
    addMessage,
  };
}

export default useConversations;
