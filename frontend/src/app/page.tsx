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
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Calendar className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  AI Event Planner
                  <Badge variant="secondary" className="text-xs bg-blue-500/20 text-blue-300 border-blue-500/30">
                    <Sparkles className="w-3 h-3 mr-1" />
                    Beta
                  </Badge>
                </h1>
                <p className="text-sm text-slate-400">
                  Your intelligent event planning companion
                </p>
              </div>
            </div>
            
            <div className="hidden sm:flex items-center gap-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                <span className="text-xs text-green-400 font-medium">Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[3fr_1fr] gap-6">
          {/* Chat Panel */}
          <div className="min-h-0">
            <Card className="h-[calc(100vh-180px)] flex flex-col bg-slate-900/50 border-slate-800 backdrop-blur-sm shadow-2xl">
              <CardHeader className="pb-4 border-b border-slate-800">
                <CardTitle className="text-xl font-semibold text-white">Conversation</CardTitle>
                <CardDescription className="text-slate-400">
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

