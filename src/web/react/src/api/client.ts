/**
 * API client for Mistral Chat React frontend
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  Conversation,
  ConversationCreate,
  ConversationUpdate,
  Message,
  MessageCreate,
  GenerationParams,
  GenerateRequest,
  GenerateResponse,
  ModelStatus,
  QuantizationMethod,
  HealthCheckResponse,
  ConversationsResponse,
  MessagesResponse,
  ModelLoadResponse,
} from '../types';

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Create axios instance with default configuration
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle errors globally
    console.error('API Error:', error.message);
    return Promise.reject(error);
  }
);

// ============================================================================
// Health Check
// ============================================================================

export const healthApi = {
  check: async (): Promise<HealthCheckResponse> => {
    const response = await api.get<HealthCheckResponse>('/api/health');
    return response.data;
  },
};

// ============================================================================
// Conversations API
// ============================================================================

export const conversationsApi = {
  // List all conversations
  list: async (limit: number = 50): Promise<Conversation[]> => {
    const response = await api.get<ConversationsResponse>('/api/conversations', {
      params: { limit },
    });
    return response.data.conversations;
  },

  // Create a new conversation
  create: async (data: ConversationCreate = {}): Promise<{ id: number }> => {
    const response = await api.post<{ id: number }>('/api/conversations', data);
    return response.data;
  },

  // Get a specific conversation
  get: async (id: number): Promise<Conversation> => {
    const response = await api.get<Conversation>(`/api/conversations/${id}`);
    return response.data;
  },

  // Update conversation title
  update: async (id: number, data: ConversationUpdate): Promise<Conversation> => {
    const response = await api.put<Conversation>(`/api/conversations/${id}`, data);
    return response.data;
  },

  // Delete a conversation
  delete: async (id: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete<{ success: boolean; message: string }>(
      `/api/conversations/${id}`
    );
    return response.data;
  },
};

// ============================================================================
// Messages API
// ============================================================================

export const messagesApi = {
  // Get all messages for a conversation
  list: async (convId: number): Promise<Message[]> => {
    const response = await api.get<MessagesResponse>(`/api/conversations/${convId}/messages`);
    return response.data.messages;
  },

  // Add a message to a conversation
  create: async (convId: number, message: MessageCreate): Promise<{ id: number }> => {
    const response = await api.post<{ id: number }>(
      `/api/conversations/${convId}/messages`,
      message
    );
    return response.data;
  },

  // Delete a message (not implemented in backend yet)
  delete: async (msgId: number): Promise<{ success: boolean }> => {
    const response = await api.delete<{ success: boolean }>(`/api/messages/${msgId}`);
    return response.data;
  },
};

// ============================================================================
// Model API
// ============================================================================

export const modelApi = {
  // Get model status
  getStatus: async (): Promise<ModelStatus> => {
    const response = await api.get<ModelStatus>('/api/model/status');
    return response.data;
  },

  // Load model
  load: async (quantMethod: QuantizationMethod = 'fp8'): Promise<ModelLoadResponse> => {
    const response = await api.post<ModelLoadResponse>('/api/model/load', null, {
      params: { quant_method: quantMethod },
    });
    return response.data;
  },

  // Unload model
  unload: async (): Promise<{ status: string }> => {
    const response = await api.post<{ status: string }>('/api/model/unload');
    return response.data;
  },

  // Get quantization options
  getQuantizationOptions: async (): Promise<{
    options: QuantizationMethod[];
    descriptions: Record<QuantizationMethod, string>;
  }> => {
    const response = await api.get<{
      options: QuantizationMethod[];
      descriptions: Record<QuantizationMethod, string>;
    }>('/api/model/quantization-options');
    return response.data;
  },

  // Get default generation parameters
  getDefaultParams: async (): Promise<GenerationParams> => {
    const response = await api.get<GenerationParams>('/api/model/default-params');
    return response.data;
  },
};

// ============================================================================
// Generation API
// ============================================================================

export const generationApi = {
  // Generate a response for a conversation
  generate: async (
    convId: number,
    request: GenerateRequest = {}
  ): Promise<GenerateResponse> => {
    const response = await api.post<GenerateResponse>(
      `/api/conversations/${convId}/generate`,
      request
    );
    return response.data;
  },
};

// ============================================================================
// WebSocket Client
// ============================================================================

let socket: WebSocket | null = null;
let messageCallback: ((message: any) => void) | null = null;
let errorCallback: ((error: string) => void) | null = null;

export const websocketApi = {
  // Connect to WebSocket
  connect: (convId: number, onMessage: (message: any) => void, onError: (error: string) => void): void => {
    // Close existing connection
    if (socket) {
      socket.close();
    }

    messageCallback = onMessage;
    errorCallback = onError;

    // Create WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = import.meta.env.VITE_API_PORT || 8000;
    const wsUrl = `${protocol}//${host}:${port}/ws/chat/${convId}`;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (messageCallback) {
          messageCallback(data);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      if (errorCallback) {
        errorCallback('WebSocket connection error');
      }
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };
  },

  // Disconnect from WebSocket
  disconnect: (): void => {
    if (socket) {
      socket.close();
      socket = null;
    }
    messageCallback = null;
    errorCallback = null;
  },

  // Send a message through WebSocket
  send: (data: any): void => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected');
    }
  },

  // Check if WebSocket is connected
  isConnected: (): boolean => {
    return socket !== null && socket.readyState === WebSocket.OPEN;
  },
};

// ============================================================================
// Main API Client
// ============================================================================

export const chatApi = {
  health: healthApi,
  conversations: conversationsApi,
  messages: messagesApi,
  model: modelApi,
  generation: generationApi,
  websocket: websocketApi,
};

export default chatApi;
