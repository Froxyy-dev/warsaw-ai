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
        return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'in_progress':
        return <Clock className="w-5 h-5 text-blue-400 animate-pulse" />;
      case 'skipped':
        return <XCircle className="w-5 h-5 text-slate-500" />;
      default:
        return <Circle className="w-5 h-5 text-slate-600" />;
    }
  };

  const getStatusBadge = (status: TaskResult['status']) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-600 hover:bg-green-700">Booked</Badge>;
      case 'no_answer':
        return <Badge variant="secondary">No Answer</Badge>;
      case 'rejected':
        return <Badge variant="destructive">Rejected</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Pipeline Steps */}
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <ClipboardList className="w-4 h-4 text-white" />
            </div>
            Event Planning Pipeline
          </CardTitle>
          <CardDescription>Track your event planning progress</CardDescription>
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
                      step.status === 'completed' ? "bg-green-400/30" : "bg-slate-700/50"
                    )} 
                  />
                )}
                
                {/* Step content */}
                <div
                  className={cn(
                    "flex gap-3 p-3 rounded-lg transition-all",
                    step.status === 'in_progress' && "bg-blue-500/10 border border-blue-500/20",
                    step.status === 'completed' && "opacity-70 hover:opacity-100"
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
                        step.status === 'completed' && "text-slate-300",
                        step.status === 'in_progress' && "text-blue-300",
                        step.status === 'pending' && "text-slate-500"
                      )}>
                        {step.title}
                      </h3>
                    </div>
                    <p className={cn(
                      "text-xs mt-1",
                      step.status === 'completed' && "text-slate-400",
                      step.status === 'in_progress' && "text-blue-400/80",
                      step.status === 'pending' && "text-slate-600"
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
        <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                <FileText className="w-4 h-4 text-white" />
              </div>
              Results & Tasks
            </CardTitle>
            <CardDescription>
              {results.length} {results.length === 1 ? 'result' : 'results'} from venue and bakery contacts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 transition-all"
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                        {result.type === 'venue' ? (
                          <MapPin className="w-5 h-5 text-blue-400" />
                        ) : (
                          <Cake className="w-5 h-5 text-pink-400" />
                        )}
                      </div>
                      <div>
                        <h4 className="font-semibold text-white text-sm">{result.placeName}</h4>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {result.type === 'venue' ? 'Venue' : 'Bakery'}
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(result.status)}
                  </div>
                  
                  {result.details && (
                    <div className="space-y-1 mb-3">
                      {result.date && (
                        <div className="text-xs text-slate-300">
                          📅 {result.date} {result.time && `at ${result.time}`}
                        </div>
                      )}
                      {result.people && (
                        <div className="text-xs text-slate-300">
                          👥 {result.people} people
                        </div>
                      )}
                      {result.price && (
                        <div className="text-xs text-slate-300">
                          💰 {result.price}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full text-xs h-8 bg-slate-800 hover:bg-slate-700 border-slate-700"
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

