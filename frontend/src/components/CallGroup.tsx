"use client";

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Phone, ChevronDown, ChevronUp } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '@/api/types';

interface CallGroupProps {
  messages: Message[];  // Array of 1-3 messages (initiated, transcript, completed)
  timestamp: string;
}

export function CallGroup({ messages, timestamp }: CallGroupProps) {
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);
  
  // Find messages by stage
  const initiatedMsg = messages.find(m => m.metadata?.call_stage === 'initiated');
  const transcriptMsg = messages.find(m => m.metadata?.call_stage === 'transcript');
  const completedMsg = messages.find(m => m.metadata?.call_stage === 'completed');
  
  // Extract call metadata
  const placeName = initiatedMsg?.metadata?.place_name || 'miejsce';
  const phoneNumber = initiatedMsg?.metadata?.place_phone || '';
  const callSuccess = completedMsg?.metadata?.call_success;
  
  // Determine call status
  const isInProgress = !completedMsg;
  const isSuccess = callSuccess === true;
  const isFailed = callSuccess === false;
  
  // Extract content parts
  const extractInstructions = (content: string): string => {
    const match = content.match(/📝 \*\*Instrukcje dla agenta:\*\*([\s\S]+?)⏳ Czekam na połączenie/);
    return match ? match[1].trim() : '';
  };
  
  const extractTranscript = (content: string): string => {
    const match = content.match(/={60}\s*TRANSKRYPT ROZMOWY\s*={60}([\s\S]+?)={60}/);
    return match ? match[1].trim() : '';
  };
  
  const extractSummary = (content: string): string => {
    // Extract everything after the ⚠️ or ✅ emoji
    const match = content.match(/[⚠️✅] \*\*(.+?)\*\*\s+([\s\S]+)/);
    if (match) {
      return match[2].trim();
    }
    return '';
  };
  
  const instructions = initiatedMsg ? extractInstructions(initiatedMsg.content) : '';
  const transcript = transcriptMsg ? extractTranscript(transcriptMsg.content) : '';
  const summary = completedMsg ? extractSummary(completedMsg.content) : '';
  
  const formatTimestamp = (ts: string) => {
    const date = new Date(ts);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  return (
    <div className="flex w-full gap-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 justify-start">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center text-neutral-400 font-semibold text-sm">
        AI
      </div>

      {/* Call group card */}
      <div className={cn(
        "max-w-[75%] rounded-2xl px-4 py-3 text-neutral-100 rounded-bl-sm transition-all",
        isSuccess ? "bg-emerald-950/30 border border-emerald-500/20" :
        isFailed ? "bg-red-950/30 border border-red-500/20" :
        isInProgress ? "bg-[#1a1a1a] border border-emerald-500/20" :
        "bg-[#1a1a1a] border border-white/[0.06]"
      )}>
        <div className="text-xs font-semibold text-neutral-500 mb-2">
          Michał
        </div>

        {/* Call header */}
        <div className="flex items-center gap-3 mb-2">
          <div className="relative">
            <Phone className={cn(
              "w-5 h-5",
              isSuccess ? "text-emerald-500" :
              isFailed ? "text-red-500" :
              isInProgress ? "text-emerald-500 animate-pulse" :
              "text-neutral-400"
            )} />
            {isInProgress && (
              <div className="absolute inset-0 w-5 h-5 bg-emerald-500/30 rounded-full animate-ping" />
            )}
          </div>
          <div className="flex-1">
            <div className="font-semibold text-neutral-100">
              {isInProgress && `⏳ Dzwonię do ${placeName}`}
              {isSuccess && `✅ Sukces: ${placeName}`}
              {isFailed && `⚠️ Nie udało się: ${placeName}`}
            </div>
            {phoneNumber && isInProgress && (
              <div className="text-sm text-neutral-500">{phoneNumber}</div>
            )}
          </div>
        </div>

        {/* Summary (visible when completed) */}
        {summary && (
          <div className="text-sm text-neutral-300 leading-relaxed mb-3 bg-[#0a0a0a]/50 rounded-lg p-3 border border-white/[0.06]">
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

        {/* Collapsible details */}
        {(instructions || transcript) && (
          <div className="border-t border-white/[0.06] pt-3">
            <button
              onClick={() => setIsDetailsOpen(!isDetailsOpen)}
              className="flex items-center justify-between w-full text-sm text-neutral-400 hover:text-neutral-300 transition-colors"
            >
              <span>
                {isInProgress ? 'Szczegóły połączenia' : 'Zobacz transkrypt i szczegóły'}
              </span>
              {isDetailsOpen ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>
            
            {isDetailsOpen && (
              <div className="mt-3 space-y-3 animate-in fade-in-0 slide-in-from-top-1 duration-200">
                {/* Instructions */}
                {instructions && (
                  <div className="text-sm text-neutral-300 bg-[#0a0a0a] rounded-lg p-3 border border-white/[0.06]">
                    <div className="font-semibold text-neutral-200 mb-2 flex items-center gap-2">
                      📝 Instrukcje dla agenta
                    </div>
                    <div className="whitespace-pre-wrap leading-relaxed text-neutral-400">
                      {instructions}
                    </div>
                  </div>
                )}
                
                {/* Transcript */}
                {transcript && (
                  <div className="text-sm text-neutral-300 bg-[#0a0a0a] rounded-lg p-3 border border-white/[0.06] max-h-96 overflow-y-auto">
                    <div className="font-semibold text-neutral-200 mb-2 flex items-center gap-2">
                      📞 Transkrypt rozmowy
                    </div>
                    <div className="whitespace-pre-wrap leading-relaxed font-mono text-xs text-neutral-400">
                      {transcript}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Timestamp */}
        <div className="text-xs mt-2 opacity-50 text-left text-neutral-600">
          {formatTimestamp(timestamp)}
        </div>
      </div>
    </div>
  );
}

