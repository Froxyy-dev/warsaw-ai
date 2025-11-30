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
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              
              // Strong/bold text
              strong: ({ children }) => (
                <strong className={isUser ? "font-bold" : "font-bold text-neutral-200"}>
                  {children}
                </strong>
              ),
              
              // Lists
              ul: ({ children }) => (
                <ul className="my-2 space-y-1 list-disc list-inside">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="my-2 space-y-1 list-decimal list-inside">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="leading-relaxed">{children}</li>
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
              
              // Headings
              h1: ({ children }) => (
                <h1 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-bold mb-1 mt-2 first:mt-0">{children}</h3>
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
              
              // Blockquotes
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-neutral-700 pl-4 py-1 my-2 italic text-neutral-400">
                  {children}
                </blockquote>
              ),
            }}
          >
            {message.content}
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

