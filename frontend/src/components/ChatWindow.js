import React, { useState, useEffect, useRef } from 'react';
import './ChatWindow.css';
import { sendMessage as sendMessageApi, createConversation, getConversations, getConversation } from '../api/chatApi';

function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const initialized = useRef(false);
  const autoRefreshInterval = useRef(null);

  // Initialize - load existing conversation or prepare for new one
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const init = async () => {
      try {
        const conversations = await getConversations();
        if (conversations.length > 0) {
          // Load most recent conversation
          const conv = await getConversation(conversations[0].id);
          setConversationId(conv.id);
          setMessages(conv.messages || []);
        }
      } catch (err) {
        console.error('Failed to load conversation:', err);
      }
    };

    init();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-refresh conversation when searching
  useEffect(() => {
    if (isSearching && conversationId) {
      console.log('🔄 Starting auto-refresh (searching venues/bakeries)...');
      
      autoRefreshInterval.current = setInterval(async () => {
        try {
          console.log('🔄 Auto-refreshing conversation...');
          const conv = await getConversation(conversationId);
          setMessages(conv.messages);
          
          // Check if we're still searching by looking at last message
          const lastMsg = conv.messages[conv.messages.length - 1];
          if (lastMsg && (
              lastMsg.content.includes('🎉 Wszystko gotowe') ||
              lastMsg.content.includes('🎉 Zakończono wszystkie zadania')
          )) {
            console.log('✅ Process complete, stopping auto-refresh');
            setIsSearching(false);
          }
        } catch (err) {
          console.error('Auto-refresh failed:', err);
        }
      }, 2000); // Refresh every 2 seconds

      return () => {
        if (autoRefreshInterval.current) {
          console.log('⏹️ Stopping auto-refresh');
          clearInterval(autoRefreshInterval.current);
        }
      };
    }
  }, [isSearching, conversationId]);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const ensureConversation = async () => {
    if (conversationId) return conversationId;
    
    // Create new conversation
    const response = await createConversation();
    const newId = response.conversation.id;
    setConversationId(newId);
    return newId;
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const messageContent = inputValue.trim();
    setInputValue('');
    setError(null);

    // Optimistic update - add user message immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Ensure conversation exists
      const convId = await ensureConversation();
      console.log('Conversation ID:', convId);
      
      // Send message to backend
      console.log('Sending message:', messageContent);
      const response = await sendMessageApi(convId, messageContent);
      console.log('Got response:', response);

      // Reload entire conversation from backend
      console.log('Reloading conversation...');
      const updatedConv = await getConversation(convId);
      console.log('Updated conversation:', updatedConv);
      setMessages(updatedConv.messages || []);

      // Check if backend is processing - if so, start auto-refresh
      const lastMessage = updatedConv.messages[updatedConv.messages.length - 1];
      if (lastMessage && (
          lastMessage.content.includes('🔍 Zaczynam wyszukiwanie') ||
          lastMessage.content.includes('📞 Rozpoczynam wykonywanie')
      )) {
        console.log('🔍 Detected active processing, enabling auto-refresh');
        setIsSearching(true);
      }

    } catch (err) {
      console.error('Failed to send message:', err);
      console.error('Error details:', err.response?.data || err.message);
      setError(`Błąd: ${err.response?.data?.detail || err.message || 'Nie udało się wysłać wiadomości'}`);
      // Remove optimistic user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      // Restore input value
      setInputValue(messageContent);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pl-PL', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">👋</div>
            <h2>Cześć!</h2>
            <p>Napisz swoją pierwszą wiadomość...</p>
          </div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`message ${message.role}`}
            >
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message assistant typing">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <form className="message-input-form" onSubmit={handleSendMessage}>
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Napisz wiadomość..."
            rows="1"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={!inputValue.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatWindow;
