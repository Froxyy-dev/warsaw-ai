"use client";

import { useState, useEffect } from "react";
import { ChatWindow } from "@/components/ChatWindow";
import { PipelineView } from "@/components/PipelineView";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Sparkles } from "lucide-react";
import { getConversations, getConversation } from '@/api/chatApi';
import type { Message } from '@/api/types';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);

  // Load messages for pipeline view
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const conversations = await getConversations();
        if (conversations.length > 0) {
          const conv = await getConversation(conversations[0].id);
          setMessages(conv.messages || []);
        }
      } catch (err) {
        console.error('Failed to load messages for pipeline:', err);
      }
    };

    loadMessages();

    // Poll for updates every 10 seconds
    const interval = setInterval(loadMessages, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="border-b border-white/[0.06] bg-[#1a1a1a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-[#2a2a2a] flex items-center justify-center border border-white/[0.08]">
                <Calendar className="w-6 h-6 text-neutral-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-neutral-100 flex items-center gap-2">
                  AI Event Planner
                  <Badge variant="secondary" className="text-xs bg-neutral-800 text-neutral-400 border-white/[0.08]">
                    <Sparkles className="w-3 h-3 mr-1" />
                    Beta
                  </Badge>
                </h1>
                <p className="text-sm text-neutral-500">
                  Your intelligent event planning companion
                </p>
              </div>
            </div>
            
            <div className="hidden sm:flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                <span className="text-xs text-emerald-500 font-medium">Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,2.6fr)_minmax(0,1fr)] gap-6">
          {/* Chat Panel */}
          <div className="min-h-0">
            <Card className="h-[calc(100vh-180px)] flex flex-col bg-[#1a1a1a] border-white/[0.06] rounded-2xl">
              <CardHeader className="pb-4 border-b border-white/[0.06]">
                <CardTitle className="text-xl font-semibold text-neutral-100">Conversation</CardTitle>
                <CardDescription className="text-neutral-500">
                  Chat with your AI assistant to plan events, find venues, and coordinate everything
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col min-h-0 p-0">
                <ChatWindow />
              </CardContent>
            </Card>
          </div>

          {/* Pipeline & Status Sidebar */}
          <div className="space-y-6 lg:max-h-[calc(100vh-180px)] lg:overflow-y-auto lg:pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
            <PipelineView messages={messages} />
          </div>
        </div>
      </div>
    </main>
  );
}

