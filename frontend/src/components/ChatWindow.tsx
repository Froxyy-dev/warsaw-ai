"use client";

import React, { useState, useEffect, useRef } from 'react';
import { sendMessage as sendMessageApi, createConversation, getConversations, getConversation } from '@/api/chatApi';
import type { Message } from '@/api/types';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { SendHorizontal, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const initialized = useRef(false);
  const autoRefreshInterval = useRef<NodeJS.Timeout | null>(null);

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

  // Auto-refresh conversation when backend is processing
  useEffect(() => {
    if (isSearching && conversationId) {
      console.log('🔄 Starting auto-refresh - backend is processing...');
      
      let refreshCount = 0;
      autoRefreshInterval.current = setInterval(async () => {
        try {
          refreshCount++;
          console.log(`🔄 Auto-refresh #${refreshCount}...`);
          const conv = await getConversation(conversationId);
          
          // Update messages
          setMessages(conv.messages);
          
          // Check if we got a new assistant message
          const lastMessage = conv.messages[conv.messages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            console.log('✅ Got assistant response! Stopping auto-refresh');
            setIsLoading(false);
            setIsSearching(false);
          }
          
          // Safety: stop after 5 minutes (150 refreshes at 2s intervals)
          if (refreshCount > 150) {
            console.log('⏱️ Auto-refresh timeout - stopping');
            setIsLoading(false);
            setIsSearching(false);
          }
        } catch (err) {
          console.error('❌ Auto-refresh failed:', err);
        }
      }, 2000); // Refresh every 2 seconds

      return () => {
        if (autoRefreshInterval.current) {
          console.log('⏹️ Stopping auto-refresh');
          clearInterval(autoRefreshInterval.current);
          autoRefreshInterval.current = null;
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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const messageContent = inputValue.trim();
    setInputValue('');
    setError(null);

    // Optimistic update - add user message immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setIsSearching(true);  // Enable auto-refresh immediately

    try {
      // Ensure conversation exists
      const convId = await ensureConversation();
      console.log('✅ Conversation ID:', convId);
      
      // Send message to backend (starts processing in background)
      console.log('📤 Sending message:', messageContent);
      await sendMessageApi(convId, messageContent);
      console.log('✅ Message sent, backend is processing...');

      // Keep loading and auto-refresh active
      // Auto-refresh will update messages every 2 seconds
      // We'll stop when we detect the assistant's response
      
      // Wait a bit for initial processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // First manual refresh to get the assistant's response
      const updatedConv = await getConversation(convId);
      console.log('📥 First refresh - messages:', updatedConv.messages.length);
      setMessages(updatedConv.messages || []);
      
      // Check if assistant has responded
      const hasAssistantResponse = updatedConv.messages.some(
        (msg, idx) => msg.role === 'assistant' && idx > messages.length - 1
      );
      
      if (!hasAssistantResponse) {
        console.log('⏳ Waiting for assistant response... auto-refresh will continue');
        // Auto-refresh will keep running until isSearching is set to false
      } else {
        console.log('✅ Got assistant response');
        setIsLoading(false);
        setIsSearching(false);
      }

    } catch (err: any) {
      console.error('❌ Failed to send message:', err);
      console.error('Error details:', err.response?.data || err.message);
      setError(`Error: ${err.response?.data?.detail || err.message || 'Failed to send message'}`);
      // Remove optimistic user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      // Restore input value
      setInputValue(messageContent);
      setIsLoading(false);
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="text-6xl opacity-50">👋</div>
            <div>
              <h2 className="text-2xl font-semibold text-white mb-2">Welcome!</h2>
              <p className="text-slate-400">
                Start a conversation to plan events, search venues, or get assistance
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex w-full",
                  message.role === 'user' ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[75%] rounded-2xl px-4 py-3 shadow-lg",
                    message.role === 'user'
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : "bg-slate-800 text-slate-100 rounded-bl-sm border border-slate-700"
                  )}
                >
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </div>
                  <div
                    className={cn(
                      "text-xs mt-2 opacity-60",
                      message.role === 'user' ? "text-right" : "text-left"
                    )}
                  >
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[75%] rounded-2xl rounded-bl-sm px-4 py-3 bg-slate-800 border border-slate-700">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
                      <span className="text-sm text-slate-300">
                        {isSearching ? 'Processing your request...' : 'Thinking...'}
                      </span>
                    </div>
                    {isSearching && (
                      <div className="text-xs text-slate-500">
                        This may take a few moments. The assistant is working on your request.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-6 mb-4 px-4 py-3 bg-red-900/50 border border-red-800 rounded-lg">
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {/* Input Form */}
      <div className="border-t border-slate-800 p-6">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <Textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="resize-none bg-slate-800 border-slate-700 focus-visible:ring-blue-500 text-white placeholder:text-slate-500 min-h-[60px] max-h-[200px]"
            rows={1}
          />
          <Button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            size="icon"
            className="h-[60px] w-[60px] rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <SendHorizontal className="w-5 h-5" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}

