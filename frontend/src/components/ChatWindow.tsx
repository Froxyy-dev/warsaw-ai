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
    if (!isSearching || !conversationId) {
      return;
    }

    console.log('🔄 Starting auto-refresh for conversation:', conversationId);
    console.log('📊 Current messages count:', messages.length);
    
    let refreshCount = 0;
    let previousMessageCount = messages.length;
    
    const intervalId = setInterval(async () => {
      try {
        refreshCount++;
        console.log('─────────────────────────────────────');
        console.log(`🔄 Auto-refresh #${refreshCount}`);
        console.log(`   Conversation: ${conversationId}`);
        console.log(`   Current messages: ${messages.length}`);
        console.log(`   Fetching GET /conversations/${conversationId}...`);
        
        const startFetch = Date.now();
        const conv = await getConversation(conversationId);
        const fetchDuration = Date.now() - startFetch;
        console.log(`📥 Received conversation in ${fetchDuration}ms`);
        console.log(`   Messages in response: ${conv.messages.length}`);
        
        // ALWAYS update messages in state - to jest kluczowe!
        setMessages(conv.messages);
        
        // Check if we got NEW messages
        if (conv.messages.length > previousMessageCount) {
          console.log(`✨ New messages detected! (${previousMessageCount} -> ${conv.messages.length})`);
          previousMessageCount = conv.messages.length;
          
          const lastMessage = conv.messages[conv.messages.length - 1];
          console.log('📨 Last message:', { role: lastMessage.role, preview: lastMessage.content.substring(0, 50) });
          
          // ✅ Backend tells us explicitly whether to continue refreshing
          if (lastMessage.role === 'assistant') {
            const metadata = lastMessage.metadata || {};
            
            // Check the explicit flag from backend
            const shouldContinue = metadata.should_continue_refresh;
            
            if (shouldContinue === false) {
              console.log('✅ Backend says: STOP auto-refresh (waiting for user input)');
              console.log('   Step:', metadata.step || 'unknown');
              console.log('   Metadata:', metadata);
              setIsLoading(false);
              setIsSearching(false);
              clearInterval(intervalId);
              return;
            } else if (shouldContinue === true) {
              console.log('📨 Backend says: CONTINUE auto-refresh (more messages coming)');
              console.log('   Step:', metadata.step || 'unknown');
            } else {
              // Fallback if flag not set - assume we should stop
              console.log('⚠️ No should_continue_refresh flag - assuming STOP');
              setIsLoading(false);
              setIsSearching(false);
              clearInterval(intervalId);
              return;
            }
          }
        } else {
          console.log('⏳ No new messages yet, continuing to poll...');
        }
        
        // Safety timeout: 2 minutes (24 * 5 seconds = 120 seconds)
        if (refreshCount > 24) {
          console.log('⏱️ Auto-refresh timeout after 2 minutes');
          setIsLoading(false);
          setIsSearching(false);
          clearInterval(intervalId);
        }
      } catch (err) {
        console.error('❌ Auto-refresh failed:', err);
      }
    }, 5000); // Refresh every 5 seconds (reduced from 2s to avoid race conditions)

    autoRefreshInterval.current = intervalId;

    return () => {
      console.log('⏹️ Cleanup: stopping auto-refresh');
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isSearching, conversationId, messages.length]);

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
    
    console.log('═══════════════════════════════════════');
    console.log('🚀 handleSendMessage() STARTED');
    console.log('═══════════════════════════════════════');
    
    if (!inputValue.trim() || isLoading) {
      console.log('⚠️ Aborting - empty input or already loading');
      return;
    }

    const messageContent = inputValue.trim();
    console.log('📝 Message content:', messageContent);
    console.log('📊 Current state:', {
      messagesCount: messages.length,
      conversationId,
      isLoading,
      isSearching
    });
    
    setInputValue('');
    setError(null);
    console.log('✅ Input cleared, error cleared');

    // Optimistic update - add user message immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    console.log('✅ Optimistic user message added:', userMessage.id);
    setIsLoading(true);
    console.log('✅ isLoading set to TRUE');

    try {
      console.log('──────────────────────────────────────');
      console.log('Step 1: Ensure conversation exists');
      // Ensure conversation exists
      const convId = await ensureConversation();
      console.log('✅ Conversation ID:', convId);
      console.log('──────────────────────────────────────');
      
      console.log('──────────────────────────────────────');
      console.log('Step 2: Send message to backend');
      console.log('📤 Message:', messageContent);
      console.log('📊 State before send:', {
        conversationId: convId,
        currentMessageCount: messages.length,
        isSearching,
        isLoading
      });
      
      // Start auto-refresh BEFORE sending - to catch updates
      console.log('──────────────────────────────────────');
      console.log('Step 3: Enable auto-refresh');
      setIsSearching(true);
      console.log('✅ isSearching set to TRUE');
      console.log('   Auto-refresh useEffect will trigger now');
      
      // Send the message (this triggers backend processing)
      console.log('──────────────────────────────────────');
      console.log('Step 4: POST to backend');
      console.log('⏳ Calling sendMessageApi()...');
      console.log('   URL: POST /api/chat/conversations/' + convId + '/messages');
      console.log('   Payload: { content: "' + messageContent + '" }');
      const startTime = Date.now();
      
      await sendMessageApi(convId, messageContent);
      
      const duration = Date.now() - startTime;
      console.log(`✅ sendMessageApi() completed in ${duration}ms`);
      console.log('──────────────────────────────────────');
      console.log('✅ SUCCESS - message sent!');
      console.log('🔄 Auto-refresh is active and will poll every 5s');
      console.log('═══════════════════════════════════════');

      // Note: Auto-refresh useEffect will now take over and:
      // 1. Fetch conversation every 2 seconds
      // 2. Update messages in UI
      // 3. Stop when assistant responds

    } catch (err: any) {
      console.log('═══════════════════════════════════════');
      console.error('❌❌❌ SEND MESSAGE FAILED! ❌❌❌');
      console.log('═══════════════════════════════════════');
      console.error('Error object:', err);
      console.error('Error message:', err.message);
      console.error('Error name:', err.name);
      console.error('Error code:', err.code);
      console.error('Response status:', err.response?.status);
      console.error('Response data:', err.response?.data);
      console.error('Response headers:', err.response?.headers);
      console.error('Request URL:', err.config?.url);
      console.error('Request method:', err.config?.method);
      console.error('Request data:', err.config?.data);
      console.log('═══════════════════════════════════════');
      console.error('🔍 BACKEND CRASHNĄŁ!');
      console.error('   → Sprawdź terminal gdzie uvicorn działa');
      console.error('   → Szukaj czerwonego erroru (Traceback)');
      console.error('   → Skopiuj WSZYSTKIE logi od 📥 do ❌');
      console.log('═══════════════════════════════════════');
      
      setError(`Error: ${err.response?.data?.detail || err.message || 'Failed to send message'}`);
      // Remove optimistic user message on error
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
      console.log('✅ Removed optimistic message from UI');
      // Restore input value
      setInputValue(messageContent);
      console.log('✅ Restored input value');
      setIsLoading(false);
      setIsSearching(false);
      console.log('✅ State reset: isLoading=false, isSearching=false');
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

