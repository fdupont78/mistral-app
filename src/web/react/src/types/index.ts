/**
 * Type definitions for Mistral Chat React frontend
 */

// ============================================================================
// Message Types
// ============================================================================

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface MessageCreate {
  role: 'user' | 'assistant';
  content: string;
}

// ============================================================================
// Conversation Types
// ============================================================================

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationCreate {
  title?: string;
}

export interface ConversationUpdate {
  title: string;
}

// ============================================================================
// Generation Parameters Types
// ============================================================================

export interface GenerationParams {
  max_new_tokens: number;
  temperature: number;
  do_sample: boolean;
  top_k: number;
  top_p: number;
  repetition_penalty: number;
  num_return_sequences: number;
}

export const DEFAULT_GENERATION_PARAMS: GenerationParams = {
  max_new_tokens: 512,
  temperature: 0.7,
  do_sample: true,
  top_k: 50,
  top_p: 0.92,
  repetition_penalty: 1.0,
  num_return_sequences: 1,
};

// ============================================================================
// Model Types
// ============================================================================

export interface ModelStatus {
  loaded: boolean;
  loading: boolean;
  status: string;
}

export type QuantizationMethod = 'none' | '8bit' | '4bit' | 'fp8';

export interface QuantizationOption {
  value: QuantizationMethod;
  label: string;
  description: string;
}

export const QUANTIZATION_OPTIONS: QuantizationOption[] = [
  {
    value: 'none',
    label: 'No Quantization',
    description: 'Full precision (~15GB VRAM for 3B)',
  },
  {
    value: '8bit',
    label: '8-bit',
    description: '8-bit quantization (~6-8GB VRAM)',
  },
  {
    value: '4bit',
    label: '4-bit',
    description: '4-bit quantization (~3-4GB VRAM)',
  },
  {
    value: 'fp8',
    label: 'FP8',
    description: 'FP8 quantization (NVIDIA GPUs, ~4GB VRAM)',
  },
];

// ============================================================================
// Generation Request Types
// ============================================================================

export interface GenerateRequest {
  params?: Partial<GenerationParams>;
  dry_run?: boolean;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface ConversationsResponse {
  conversations: Conversation[];
}

export interface ConversationResponse {
  conversation: Conversation;
}

export interface MessagesResponse {
  messages: Message[];
}

export interface GenerateResponse {
  response: string;
  conversation_id: number;
}

export interface ModelLoadResponse {
  status: string;
  quant_method?: QuantizationMethod;
}

export interface HealthCheckResponse {
  status: string;
  database: boolean;
  model_manager: boolean;
}

// ============================================================================
// WebSocket Types
// ============================================================================

export type WebSocketMessageType = 'response' | 'error' | 'status';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  response?: string;
  error?: string;
  conversation_id?: number;
}

export interface WebSocketRequest {
  message?: string;
  role?: 'user' | 'assistant';
  params?: Partial<GenerationParams>;
  dry_run?: boolean;
}

// ============================================================================
// Application State Types
// ============================================================================

export interface AppState {
  // Conversations
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  
  // Model
  modelStatus: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  
  // Generation
  generationParams: GenerationParams;
  isGenerating: boolean;
  
  // UI
  isSidebarOpen: boolean;
  error: string | null;
}

export interface ChatState {
  messages: Message[];
  isGenerating: boolean;
  input: string;
}

// ============================================================================
// Component Props Types
// ============================================================================

export interface ChatInterfaceProps {
  messages: Message[];
  onSend: (content: string) => void;
  isGenerating: boolean;
  modelReady: boolean;
  inputValue: string;
  onInputChange: (value: string) => void;
}

export interface SidebarProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  modelStatus: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  onNewConversation: () => void;
  onSelectConversation: (conversation: Conversation) => void;
  onDeleteConversation: (id: number) => void;
  onUpdateConversation: (id: number, title: string) => void;
  onLoadModel: (quantMethod: QuantizationMethod) => void;
  onUnloadModel: () => void;
  onToggleAutoLoad: (value: boolean) => void;
}

export interface ConversationListProps {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  onSelect: (conversation: Conversation) => void;
  onDelete: (id: number) => void;
  onUpdate: (id: number, title: string) => void;
}

export interface ModelControlsProps {
  status: ModelStatus;
  quantizationMethod: QuantizationMethod;
  autoLoadModel: boolean;
  onLoad: (quantMethod: QuantizationMethod) => void;
  onUnload: () => void;
  onToggleAutoLoad: (value: boolean) => void;
}

export interface GenerationParamsProps {
  params: GenerationParams;
  onChange: (params: GenerationParams) => void;
}

export interface MessageBubbleProps {
  message: Message;
}

// ============================================================================
// Utility Types
// ============================================================================

export type ValueOf<T> = T[keyof T];

export type SetState<T> = React.Dispatch<React.SetStateAction<T>>;
