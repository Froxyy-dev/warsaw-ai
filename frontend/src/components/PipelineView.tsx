"use client";

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  CheckCircle2, 
  Circle, 
  Clock, 
  XCircle,
  ClipboardList,
  Lightbulb,
  MessageSquare,
  MapPin,
  Phone,
  Cake,
  FileText
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Message } from '@/api/types';

interface PipelineStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
}

interface TaskResult {
  id: string;
  type: 'venue' | 'bakery';
  placeName: string;
  status: 'success' | 'no_answer' | 'rejected' | 'pending';
  details?: string;
  date?: string;
  time?: string;
  people?: number;
  price?: string;
}

interface PipelineViewProps {
  messages: Message[];
}

export function PipelineView({ messages }: PipelineViewProps) {
  // Determine pipeline state from messages
  const getPipelineState = (): PipelineStep[] => {
    // Analyze messages to determine current state
    const hasUserMessage = messages.some(m => m.role === 'user');
    const hasAssistantResponse = messages.some(m => m.role === 'assistant');
    
    // Look for specific keywords/metadata to determine progress
    const hasRequirements = messages.some(m => 
      m.content.toLowerCase().includes('event') || 
      m.content.toLowerCase().includes('party') ||
      m.content.toLowerCase().includes('celebration')
    );
    
    const hasPlanProposal = messages.some(m => 
      m.role === 'assistant' && (
        m.content.toLowerCase().includes('plan') ||
        m.content.toLowerCase().includes('suggest') ||
        m.metadata?.step === 'plan_proposed'
      )
    );
    
    const hasVenueSearch = messages.some(m => 
      m.content.toLowerCase().includes('venue') ||
      m.content.toLowerCase().includes('location') ||
      m.metadata?.step === 'venue_search'
    );
    
    const hasVenueCalls = messages.some(m => 
      m.content.toLowerCase().includes('calling') ||
      m.content.toLowerCase().includes('contacted') ||
      m.metadata?.step === 'venue_calls'
    );
    
    const hasBakerySearch = messages.some(m => 
      m.content.toLowerCase().includes('bakery') ||
      m.content.toLowerCase().includes('cake') ||
      m.metadata?.step === 'bakery_search'
    );
    
    const hasBakeryCalls = messages.some(m => 
      m.content.toLowerCase().includes('bakery') && 
      m.content.toLowerCase().includes('call')
    );
    
    const hasResults = messages.some(m => 
      m.content.toLowerCase().includes('summary') ||
      m.content.toLowerCase().includes('result') ||
      m.metadata?.complete === true
    );

    return [
      {
        id: 'requirements',
        title: 'Collect Requirements',
        description: 'Gathering event details from user',
        icon: <ClipboardList className="w-4 h-4" />,
        status: hasUserMessage ? 'completed' : 'pending'
      },
      {
        id: 'proposal',
        title: 'Propose Event Plan',
        description: 'Creating personalized event plan',
        icon: <Lightbulb className="w-4 h-4" />,
        status: hasPlanProposal ? 'completed' : (hasRequirements ? 'in_progress' : 'pending')
      },
      {
        id: 'feedback',
        title: 'Refine Plan',
        description: 'Apply user feedback and finalize',
        icon: <MessageSquare className="w-4 h-4" />,
        status: hasVenueSearch ? 'completed' : (hasPlanProposal ? 'in_progress' : 'pending')
      },
      {
        id: 'venue_search',
        title: 'Search Venues',
        description: 'Finding suitable locations',
        icon: <MapPin className="w-4 h-4" />,
        status: hasVenueCalls ? 'completed' : (hasVenueSearch ? 'in_progress' : 'pending')
      },
      {
        id: 'venue_calls',
        title: 'Contact Venues',
        description: 'Making reservation calls',
        icon: <Phone className="w-4 h-4" />,
        status: hasVenueCalls ? 'completed' : (hasVenueSearch ? 'pending' : 'pending')
      },
      {
        id: 'bakery_search',
        title: 'Search Bakeries',
        description: 'Finding cake shops',
        icon: <Cake className="w-4 h-4" />,
        status: hasBakeryCalls ? 'completed' : (hasBakerySearch ? 'in_progress' : 'pending')
      },
      {
        id: 'bakery_calls',
        title: 'Contact Bakeries',
        description: 'Ordering cakes',
        icon: <Phone className="w-4 h-4" />,
        status: hasBakeryCalls ? 'completed' : (hasBakerySearch ? 'pending' : 'pending')
      },
      {
        id: 'results',
        title: 'Summarize Results',
        description: 'Final summary and recommendations',
        icon: <FileText className="w-4 h-4" />,
        status: hasResults ? 'completed' : 'pending'
      }
    ];
  };

  // Extract task results from messages
  const getTaskResults = (): TaskResult[] => {
    // This is a placeholder - in a real implementation, you'd parse
    // the message content or metadata to extract actual results
    const results: TaskResult[] = [];
    
    // Look for venue/bakery mentions in messages
    messages.forEach(m => {
      if (m.role === 'assistant') {
        // Simple heuristic - in production, use structured metadata
        if (m.content.toLowerCase().includes('restaurant') || 
            m.content.toLowerCase().includes('venue')) {
          // Extract from message content if available
          // This is simplified - real implementation would parse structured data
        }
      }
    });
    
    return results;
  };

  const steps = getPipelineState();
  const results = getTaskResults();

  const getStatusIcon = (status: PipelineStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case 'in_progress':
        return <Clock className="w-5 h-5 text-neutral-400 animate-pulse" />;
      case 'skipped':
        return <XCircle className="w-5 h-5 text-neutral-700" />;
      default:
        return <Circle className="w-5 h-5 text-neutral-800" />;
    }
  };

  const getStatusBadge = (status: TaskResult['status']) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/30">Booked</Badge>;
      case 'no_answer':
        return <Badge className="bg-neutral-800/50 hover:bg-neutral-800 text-neutral-400 border-white/[0.06]">No Answer</Badge>;
      case 'rejected':
        return <Badge className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30">Rejected</Badge>;
      default:
        return <Badge className="bg-neutral-900/50 border-white/[0.06] text-neutral-500">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Pipeline Steps */}
      <Card className="bg-[#1a1a1a] border-white/[0.06] rounded-2xl">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2 text-neutral-100">
            <div className="w-8 h-8 rounded-lg bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center">
              <ClipboardList className="w-4 h-4 text-neutral-400" />
            </div>
            Event Planning Pipeline
          </CardTitle>
          <CardDescription className="text-neutral-500">Track your event planning progress</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {steps.map((step, index) => (
              <div key={step.id} className="relative">
                {/* Connecting line */}
                {index < steps.length - 1 && (
                  <div 
                    className={cn(
                      "absolute left-[10px] top-9 w-[2px] h-[calc(100%+4px)]",
                      step.status === 'completed' ? "bg-emerald-500/20" : "bg-neutral-800/50"
                    )} 
                  />
                )}
                
                {/* Step content */}
                <div
                  className={cn(
                    "flex gap-3 p-3 rounded-lg transition-all",
                    step.status === 'in_progress' && "bg-neutral-800/30 border border-neutral-700/50",
                    step.status === 'completed' && "opacity-60 hover:opacity-100"
                  )}
                >
                  {/* Status icon */}
                  <div className="flex-shrink-0 mt-0.5">
                    {getStatusIcon(step.status)}
                  </div>
                  
                  {/* Step info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="flex-shrink-0 opacity-60">
                        {step.icon}
                      </div>
                      <h3 className={cn(
                        "text-sm font-semibold",
                        step.status === 'completed' && "text-neutral-300",
                        step.status === 'in_progress' && "text-neutral-200",
                        step.status === 'pending' && "text-neutral-600"
                      )}>
                        {step.title}
                      </h3>
                    </div>
                    <p className={cn(
                      "text-xs mt-1",
                      step.status === 'completed' && "text-neutral-500",
                      step.status === 'in_progress' && "text-neutral-400",
                      step.status === 'pending' && "text-neutral-700"
                    )}>
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Task Results */}
      {results.length > 0 && (
        <Card className="bg-[#1a1a1a] border-white/[0.06] rounded-2xl">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-neutral-100">
              <div className="w-8 h-8 rounded-lg bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center">
                <FileText className="w-4 h-4 text-neutral-400" />
              </div>
              Results & Tasks
            </CardTitle>
            <CardDescription className="text-neutral-500">
              {results.length} {results.length === 1 ? 'result' : 'results'} from venue and bakery contacts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-4 rounded-xl bg-[#0a0a0a] border border-white/[0.06] hover:border-white/[0.1] transition-all"
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-[#2a2a2a] border border-white/[0.08] flex items-center justify-center">
                        {result.type === 'venue' ? (
                          <MapPin className="w-5 h-5 text-neutral-400" />
                        ) : (
                          <Cake className="w-5 h-5 text-neutral-400" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-semibold text-neutral-200 text-sm">{result.placeName}</h4>
                        <p className="text-xs text-neutral-500 mt-0.5">
                          {result.type === 'venue' ? 'Venue' : 'Bakery'}
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(result.status)}
                  </div>
                  
                  {result.details && (
                    <div className="space-y-1 mb-3">
                      {result.date && (
                        <div className="text-xs text-neutral-400">
                          📅 {result.date} {result.time && `at ${result.time}`}
                        </div>
                      )}
                      {result.people && (
                        <div className="text-xs text-neutral-400">
                          👥 {result.people} people
                        </div>
                      )}
                      {result.price && (
                        <div className="text-xs text-neutral-400">
                          💰 {result.price}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full text-xs h-8 bg-[#2a2a2a] hover:bg-[#333333] border-white/[0.08] text-neutral-400"
                  >
                    View Transcript
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

    </div>
  );
}

