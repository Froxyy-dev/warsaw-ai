"use client";

import { ChatWindow } from "@/components/ChatWindow";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="text-4xl">💬</div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">
                AI Chat Assistant
              </h1>
              <p className="text-sm text-slate-400">
                Your intelligent planning companion
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Panel - Takes 3 columns on large screens */}
          <div className="lg:col-span-3">
            <Card className="h-[calc(100vh-180px)] flex flex-col bg-slate-900/50 border-slate-800">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl">Chat</CardTitle>
                <CardDescription>
                  Ask me anything about planning events, searching venues, or organizing tasks
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col min-h-0 p-0">
                <ChatWindow />
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Takes 1 column */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
                <CardDescription>Common tasks and shortcuts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <button className="w-full text-left px-4 py-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50">
                  <div className="text-sm font-medium text-white">🎉 Plan an Event</div>
                  <div className="text-xs text-slate-400 mt-1">
                    Start planning your next party or gathering
                  </div>
                </button>
                <button className="w-full text-left px-4 py-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50">
                  <div className="text-sm font-medium text-white">📍 Search Venues</div>
                  <div className="text-xs text-slate-400 mt-1">
                    Find the perfect location for your event
                  </div>
                </button>
                <button className="w-full text-left px-4 py-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors border border-slate-700/50">
                  <div className="text-sm font-medium text-white">✅ View Tasks</div>
                  <div className="text-xs text-slate-400 mt-1">
                    Check your planned tasks and activities
                  </div>
                </button>
              </CardContent>
            </Card>

            {/* Status Card */}
            <Card className="bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-lg">Status</CardTitle>
                <CardDescription>System information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Connection</span>
                    <span className="flex items-center gap-2 text-green-400">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                      Connected
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">API Status</span>
                    <span className="text-green-400">Operational</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}

