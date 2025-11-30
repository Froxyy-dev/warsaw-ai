"use client";

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import type { Message } from '@/api/types';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Preprocessing: Clean up [ACTION GROUP X] markers
  const processContent = (content: string): string => {
    // Remove [ACTION GROUP X] completely and just keep the content
    // This removes the technical marker but keeps the structure
    return content.replace(/\[ACTION GROUP \d+\]\s*/g, '');
  };

  return (
    <div
      className={cn(
        "flex w-full gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Avatar for assistant */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center text-neutral-400 font-semibold text-sm">
          AI
        </div>
      )}

      {/* Message content */}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 transition-all",
          isUser
            ? "bg-[#2a2a2a] text-neutral-100 rounded-br-sm border border-white/[0.08]"
            : "bg-[#1a1a1a] text-neutral-100 rounded-bl-sm border border-white/[0.06]"
        )}
      >
        {/* Label */}
        {!isUser && (
          <div className="text-xs font-semibold text-neutral-500 mb-2">
            Michał
          </div>
        )}

        {/* Content with markdown support */}
        <div className={cn(
          "text-[15px] leading-relaxed prose prose-invert max-w-none",
          isUser ? "prose-p:text-white prose-strong:text-white prose-li:text-white" : ""
        )}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Paragraphs
              p: ({ children }) => (
                <p className="mb-2.5 last:mb-0 leading-relaxed">{children}</p>
              ),
              
              // Strong/bold text
              strong: ({ children }) => (
                <strong className={isUser ? "font-bold" : "font-bold text-neutral-200"}>
                  {children}
                </strong>
              ),
              
              // Lists - styled as cards/tiles
              ul: ({ children }) => (
                <ul className="my-3 space-y-2">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="my-3 space-y-2">{children}</ol>
              ),
              li: ({ children }) => (
                <li className={cn(
                  "leading-relaxed px-3 py-2.5 rounded-lg transition-colors",
                  isUser 
                    ? "bg-[#1a1a1a]/50 border border-white/[0.08]" 
                    : "bg-[#0a0a0a] border border-white/[0.06] hover:border-white/[0.12]"
                )}>
                  <div className="flex items-start gap-2">
                    <span className="text-emerald-500 mt-0.5 flex-shrink-0">•</span>
                    <span className="flex-1">{children}</span>
                  </div>
                </li>
              ),
              
              // Links
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={cn(
                    "underline underline-offset-2 transition-colors",
                    isUser 
                      ? "hover:text-neutral-200" 
                      : "text-neutral-400 hover:text-neutral-300"
                  )}
                >
                  {children}
                </a>
              ),
              
              // Headings - styled as section separators
              h1: ({ children }) => (
                <h1 className="text-lg font-bold mb-3 mt-4 first:mt-0 pb-2 border-b border-white/[0.08]">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-bold mb-3 mt-4 first:mt-0 pb-2 border-b border-white/[0.06] text-neutral-200">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold mb-2 mt-3 first:mt-0 text-neutral-300">
                  {children}
                </h3>
              ),
              
              // Code blocks
              code: ({ className, children }) => {
                const isInline = !className;
                return isInline ? (
                  <code className="px-1.5 py-0.5 rounded bg-[#0a0a0a] text-neutral-300 text-sm font-mono border border-white/[0.06]">
                    {children}
                  </code>
                ) : (
                  <code className="block px-3 py-2 rounded-lg bg-[#0a0a0a] text-neutral-300 text-sm font-mono overflow-x-auto my-2 border border-white/[0.06]">
                    {children}
                  </code>
                );
              },
              
              // Blockquotes - styled as info panels
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-emerald-500/30 bg-emerald-500/5 px-4 py-3 my-3 rounded-r-lg">
                  <div className="text-neutral-300 italic">
                    {children}
                  </div>
                </blockquote>
              ),
            }}
          >
            {processContent(message.content)}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            "text-xs mt-2 opacity-50",
            isUser ? "text-right text-neutral-500" : "text-left text-neutral-600"
          )}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>

      {/* Avatar for user */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center text-neutral-400 font-semibold text-sm">
          You
        </div>
      )}
    </div>
  );
}

