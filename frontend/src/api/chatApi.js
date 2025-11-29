import api from './axios';

/**
 * API client for chat functionality
 */

/**
 * Create a new conversation
 * @returns {Promise<Object>} Created conversation
 */
export const createConversation = async () => {
  const response = await api.post('/chat/conversations/', {});
  return response.data;
};

/**
 * Get list of all conversations
 * @returns {Promise<Array>} List of conversation metadata
 */
export const getConversations = async () => {
  const response = await api.get('/chat/conversations/');
  return response.data;
};

/**
 * Get a specific conversation with full message history
 * @param {string} conversationId - ID of the conversation
 * @returns {Promise<Object>} Conversation with messages
 */
export const getConversation = async (conversationId) => {
  const response = await api.get(`/chat/conversations/${conversationId}`);
  return response.data;
};

/**
 * Send a message to a conversation
 * @param {string} conversationId - ID of the conversation
 * @param {string} content - Message content
 * @returns {Promise<Object>} AI response message
 */
export const sendMessage = async (conversationId, content) => {
  const response = await api.post(
    `/chat/conversations/${conversationId}/messages`,
    { content }
  );
  return response.data;
};

/**
 * Delete a conversation
 * @param {string} conversationId - ID of the conversation
 * @returns {Promise<Object>} Success response
 */
export const deleteConversation = async (conversationId) => {
  const response = await api.delete(`/chat/conversations/${conversationId}`);
  return response.data;
};

/**
 * Get messages from a conversation with pagination
 * @param {string} conversationId - ID of the conversation
 * @param {number} limit - Maximum number of messages
 * @param {number} offset - Number of messages to skip
 * @returns {Promise<Array>} List of messages
 */
export const getMessages = async (conversationId, limit = 50, offset = 0) => {
  const response = await api.get(
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

