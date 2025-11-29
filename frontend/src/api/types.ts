export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
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

