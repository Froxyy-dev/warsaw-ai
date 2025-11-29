export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    step?: string;
    error?: boolean;
    critical_error?: boolean;
    complete?: boolean;
    should_continue_refresh?: boolean;  // Backend tells frontend whether to keep auto-refreshing
    [key: string]: any;
  };
}

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationMetadata {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface CreateConversationResponse {
  conversation: Conversation;
}

export interface SendMessageResponse {
  message: Message;
}

