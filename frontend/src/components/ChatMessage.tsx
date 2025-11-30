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
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm shadow-lg">
          AI
        </div>
      )}

      {/* Message content */}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 shadow-lg transition-all hover:shadow-xl",
          isUser
            ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-br-sm"
            : "bg-slate-800/80 text-slate-100 rounded-bl-sm border border-slate-700/50 backdrop-blur-sm"
        )}
      >
        {/* Label */}
        {!isUser && (
          <div className="text-xs font-semibold text-blue-400 mb-2">
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
                <strong className={isUser ? "font-bold" : "font-bold text-blue-300"}>
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
                      ? "hover:text-blue-200" 
                      : "text-blue-400 hover:text-blue-300"
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
                  <code className="px-1.5 py-0.5 rounded bg-slate-900/50 text-blue-300 text-sm font-mono">
                    {children}
                  </code>
                ) : (
                  <code className="block px-3 py-2 rounded-lg bg-slate-900/50 text-blue-300 text-sm font-mono overflow-x-auto my-2">
                    {children}
                  </code>
                );
              },
              
              // Blockquotes
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-blue-500 pl-4 py-1 my-2 italic">
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
            "text-xs mt-2 opacity-60",
            isUser ? "text-right text-blue-100" : "text-left text-slate-400"
          )}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>

      {/* Avatar for user */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-semibold text-sm shadow-lg">
          You
        </div>
      )}
    </div>
  );
}

