import api from './axios';
import type {
  Conversation,
  ConversationMetadata,
  CreateConversationResponse,
  SendMessageResponse,
  Message,
} from './types';

/**
 * API client for chat functionality
 */

/**
 * Create a new conversation
 */
export const createConversation = async (): Promise<CreateConversationResponse> => {
  const response = await api.post<CreateConversationResponse>('/chat/conversations/', {});
  return response.data;
};

/**
 * Get list of all conversations
 */
export const getConversations = async (): Promise<ConversationMetadata[]> => {
  const response = await api.get<ConversationMetadata[]>('/chat/conversations/');
  return response.data;
};

/**
 * Get a specific conversation with full message history
 */
export const getConversation = async (conversationId: string): Promise<Conversation> => {
  const response = await api.get<Conversation>(`/chat/conversations/${conversationId}`);
  return response.data;
};

/**
 * Send a message to a conversation
 */
export const sendMessage = async (
  conversationId: string,
  content: string
): Promise<SendMessageResponse> => {
  const response = await api.post<SendMessageResponse>(
    `/chat/conversations/${conversationId}/messages`,
    { content }
  );
  return response.data;
};

/**
 * Delete a conversation
 */
export const deleteConversation = async (conversationId: string): Promise<void> => {
  await api.delete(`/chat/conversations/${conversationId}`);
};

/**
 * Get messages from a conversation with pagination
 */
export const getMessages = async (
  conversationId: string,
  limit = 50,
  offset = 0
): Promise<Message[]> => {
  const response = await api.get<Message[]>(
    `/chat/conversations/${conversationId}/messages`,
    { params: { limit, offset } }
  );
  return response.data;
};

export default {
  createConversation,
  getConversations,
  getConversation,
  sendMessage,
  deleteConversation,
  getMessages,
};

