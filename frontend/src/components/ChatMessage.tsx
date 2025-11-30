"use client";

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';
import type { Message } from '@/api/types';
import { ChevronDown, ChevronUp, Phone } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Detect if this is a "calling in progress" message
  const isCallingMessage = message.content.includes('📞 Dzwonię do:') && message.content.includes('⏳ Czekam na połączenie');
  
  // Detect if this is a transcript message
  const isTranscriptMessage = message.content.includes('TRANSKRYPT ROZMOWY') || message.content.includes('Zakończono rozmowę');

  // Preprocessing: Clean up [ACTION GROUP X] markers
  const processContent = (content: string): string => {
    // Remove [ACTION GROUP X] completely and just keep the content
    // This removes the technical marker but keeps the structure
    return content.replace(/\[ACTION GROUP \d+\]\s*/g, '');
  };

  // Extract place name from calling message (handles markdown bold)
  const extractPlaceName = (content: string): string => {
    const match = content.match(/📞 Dzwonię do:\s*\*\*(.+?)\*\*/);
    if (match) return match[1];
    // Fallback without markdown
    const fallbackMatch = content.match(/📞 Dzwonię do:\s*(.+?)(?:\n|📱)/);
    return fallbackMatch ? fallbackMatch[1].trim() : 'miejsce';
  };

  // Extract place name from transcript message (handles markdown bold)
  const extractTranscriptPlaceName = (content: string): string => {
    const match = content.match(/📞 Zakończono rozmowę z\s*\*\*(.+?)\*\*/);
    if (match) return match[1];
    // Fallback without markdown
    const fallbackMatch = content.match(/📞 Zakończono rozmowę z\s*(.+?)(?:\n|$)/);
    return fallbackMatch ? fallbackMatch[1].trim() : 'miejsce';
  };

  // Render special UI for transcript messages
  if (isTranscriptMessage && !isUser) {
    const placeName = extractTranscriptPlaceName(message.content);
    
    // Extract transcript content (between ===== lines)
    const transcriptMatch = message.content.match(/={60}\s*TRANSKRYPT ROZMOWY([\s\S]+?)={60}/);
    const transcript = transcriptMatch ? transcriptMatch[1].trim() : '';
    
    // Extract summary (everything after the transcript)
    const summaryMatch = message.content.match(/={60}\s*\n([\s\S]+)$/);
    const summary = summaryMatch ? summaryMatch[1].trim() : '';
    
    // Detect if call was successful or failed
    const isSuccess = message.content.includes('✅');
    const isFailed = message.content.includes('⚠️') || message.content.includes('❌');

    return (
      <div className="flex w-full gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 justify-start">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center text-neutral-400 font-semibold text-sm">
          AI
        </div>

        {/* Transcript card */}
        <div className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3 text-neutral-100 rounded-bl-sm transition-all",
          isSuccess ? "bg-emerald-950/30 border border-emerald-500/20" :
          isFailed ? "bg-red-950/30 border border-red-500/20" :
          "bg-[#1a1a1a] border border-white/[0.06]"
        )}>
          <div className="text-xs font-semibold text-neutral-500 mb-2">
            Michał
          </div>

          {/* Call result header */}
          <div className="flex items-center gap-3 mb-3">
            <Phone className={cn(
              "w-5 h-5",
              isSuccess ? "text-emerald-500" :
              isFailed ? "text-red-500" :
              "text-neutral-400"
            )} />
            <div className="font-semibold text-neutral-100">
              Zakończono rozmowę z {placeName}
            </div>
          </div>

          {/* Summary (always visible) */}
          {summary && (
            <div className="text-sm text-neutral-300 leading-relaxed mb-3">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  p: ({ children }) => <p className="mb-1.5 last:mb-0">{children}</p>,
                  strong: ({ children }) => <strong className="font-bold text-neutral-200">{children}</strong>,
                }}
              >
                {summary}
              </ReactMarkdown>
            </div>
          )}

          {/* Collapsible transcript */}
          {transcript && (
            <div className="border-t border-white/[0.06] pt-3">
              <button
                onClick={() => setIsDetailsOpen(!isDetailsOpen)}
                className="flex items-center justify-between w-full text-sm text-neutral-400 hover:text-neutral-300 transition-colors"
              >
                <span>Zobacz transkrypt rozmowy</span>
                {isDetailsOpen ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
              
              {isDetailsOpen && (
                <div className="mt-3 text-sm text-neutral-300 bg-[#0a0a0a] rounded-lg p-3 border border-white/[0.06] animate-in fade-in-0 slide-in-from-top-1 duration-200 max-h-96 overflow-y-auto">
                  <div className="whitespace-pre-wrap leading-relaxed font-mono text-xs">
                    {transcript}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Timestamp */}
          <div className="text-xs mt-2 opacity-50 text-left text-neutral-600">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }

  // Render special UI for calling messages
  if (isCallingMessage && !isUser) {
    const placeName = extractPlaceName(message.content);
    const phoneMatch = message.content.match(/📱 Numer: (.+?)(?:\n|$)/);
    const phoneNumber = phoneMatch ? phoneMatch[1] : '';
    
    // Extract instructions (everything between 📝 and ⏳)
    const instructionsMatch = message.content.match(/📝 Instrukcje dla agenta:([\s\S]+?)⏳ Czekam na połączenie/);
    const instructions = instructionsMatch ? instructionsMatch[1].trim() : '';

    return (
      <div className="flex w-full gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 justify-start">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center text-neutral-400 font-semibold text-sm">
          AI
        </div>

        {/* Calling card */}
        <div className="max-w-[75%] rounded-2xl px-4 py-3 bg-[#1a1a1a] text-neutral-100 rounded-bl-sm border border-emerald-500/20 transition-all">
          <div className="text-xs font-semibold text-neutral-500 mb-2">
            Michał
          </div>

          {/* Pulsing phone icon + place name */}
          <div className="flex items-center gap-3 mb-3">
            <div className="relative">
              <Phone className="w-5 h-5 text-emerald-500 animate-pulse" />
              <div className="absolute inset-0 w-5 h-5 bg-emerald-500/30 rounded-full animate-ping" />
            </div>
            <div>
              <div className="font-semibold text-neutral-100">Dzwonię do {placeName}</div>
              {phoneNumber && (
                <div className="text-sm text-neutral-500">{phoneNumber}</div>
              )}
            </div>
          </div>

          {/* Collapsible details */}
          {instructions && (
            <div className="border-t border-white/[0.06] pt-3">
              <button
                onClick={() => setIsDetailsOpen(!isDetailsOpen)}
                className="flex items-center justify-between w-full text-sm text-neutral-400 hover:text-neutral-300 transition-colors"
              >
                <span>Szczegóły połączenia</span>
                {isDetailsOpen ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
              
              {isDetailsOpen && (
                <div className="mt-3 text-sm text-neutral-300 bg-[#0a0a0a] rounded-lg p-3 border border-white/[0.06] animate-in fade-in-0 slide-in-from-top-1 duration-200">
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {instructions}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Timestamp */}
          <div className="text-xs mt-2 opacity-50 text-left text-neutral-600">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  }

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

