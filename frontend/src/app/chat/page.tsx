'use client';

import React, { useEffect, useRef, useState } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { conversationService } from '@/services/api/conversations';
import { Conversation, ConversationDetail, ConversationMessage } from '@/types/conversation';
import { ApiError } from '@/services/api/errors';

const PROMPT_SUGGESTIONS = [
  {
    title: 'Design Learning Roadmap',
    description: 'Structure an end-to-end plan for Distributed Systems',
    prompt: 'Help me design a comprehensive, production-grade learning roadmap for Distributed Systems. Break it into foundational, intermediate, and advanced stages.',
  },
  {
    title: 'Clarify Technical Concept',
    description: 'Explain PostgreSQL MVCC & transaction isolation',
    prompt: 'Explain how PostgreSQL implements Multi-Version Concurrency Control (MVCC) and how snapshot isolation prevents dirty reads.',
  },
  {
    title: 'Best Practices & Architecture',
    description: 'Review microservice resilience and circuit breakers',
    prompt: 'What are the essential architectural patterns for resilient microservices? Explain circuit breakers, retry backoffs, and fallback strategies.',
  },
  {
    title: 'Interview & Deep Dive',
    description: 'Prepare for Senior Backend engineering topics',
    prompt: 'Give me 3 deep-dive architectural interview questions on caching strategies and high-throughput write pipelines with Redis and Kafka.',
  },
];

function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) {
    return err.detail || err.message;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return fallback;
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [activeDetail, setActiveDetail] = useState<ConversationDetail | null>(null);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [inputContent, setInputContent] = useState('');
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const activeDetailRef = useRef<ConversationDetail | null>(null);

  // Keep ref synchronized with state to prevent race conditions during message streaming
  useEffect(() => {
    activeDetailRef.current = activeDetail;
  }, [activeDetail]);

  // Auto-scroll to bottom of message thread
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeDetail?.messages, isSending]);

  // Load conversation list on mount
  useEffect(() => {
    let isMounted = true;
    async function fetchList() {
      try {
        setIsLoadingList(true);
        const list = await conversationService.listConversations();
        if (isMounted) {
          setConversations(list);
          if (list.length > 0) {
            setActiveId(list[0].id);
          }
        }
      } catch (err) {
        if (isMounted) {
          setErrorBanner(getErrorMessage(err, 'Failed to load conversations.'));
        }
      } finally {
        if (isMounted) {
          setIsLoadingList(false);
        }
      }
    }
    fetchList();
    return () => {
      isMounted = false;
    };
  }, []);

  // Fetch active conversation detail when activeId changes
  useEffect(() => {
    let isMounted = true;
    async function fetchDetail() {
      if (!activeId) {
        queueMicrotask(() => {
          if (isMounted) {
            activeDetailRef.current = null;
            setActiveDetail(null);
          }
        });
        return;
      }
      // If we already have the active detail loaded for this activeId, avoid overwriting
      if (activeDetailRef.current && activeDetailRef.current.id === activeId) {
        return;
      }
      try {
        setIsLoadingDetail(true);
        setErrorBanner(null);
        const detail = await conversationService.getConversation(activeId);
        if (isMounted) {
          activeDetailRef.current = detail;
          setActiveDetail(detail);
        }
      } catch (err) {
        if (isMounted) {
          setErrorBanner(getErrorMessage(err, 'Failed to load conversation history.'));
        }
      } finally {
        if (isMounted) {
          setIsLoadingDetail(false);
        }
      }
    }
    fetchDetail();
    return () => {
      isMounted = false;
    };
  }, [activeId]);

  // Start a new conversation
  const handleNewChat = async () => {
    try {
      setErrorBanner(null);
      const newConv = await conversationService.createConversation({ title: 'New Conversation' });
      const newDetail: ConversationDetail = {
        ...newConv,
        messages: [],
      };
      activeDetailRef.current = newDetail;
      setConversations((prev) => [newConv, ...prev.filter((c) => c.id !== newConv.id)]);
      setActiveId(newConv.id);
      setActiveDetail(newDetail);
      setSidebarOpen(false);
      setTimeout(() => textareaRef.current?.focus(), 100);
    } catch (err) {
      setErrorBanner(getErrorMessage(err, 'Failed to create conversation.'));
    }
  };

  // Delete conversation
  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    try {
      await conversationService.deleteConversation(convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeId === convId) {
        const remaining = conversations.filter((c) => c.id !== convId);
        if (remaining.length > 0) {
          setActiveId(remaining[0].id);
        } else {
          setActiveId(null);
          activeDetailRef.current = null;
          setActiveDetail(null);
        }
      }
    } catch (err) {
      setErrorBanner(getErrorMessage(err, 'Failed to delete conversation.'));
    }
  };

  // Send a message
  const handleSendMessage = async (textToSend?: string) => {
    const content = (textToSend ?? inputContent).trim();
    if (!content || isSending) return;

    setErrorBanner(null);
    setInputContent('');

    let currentConvId = activeId;
    let targetConv = activeDetailRef.current;

    // Create conversation on the fly if none selected
    if (!currentConvId || !targetConv) {
      try {
        const newConv = await conversationService.createConversation({ title: 'New Conversation' });
        currentConvId = newConv.id;
        targetConv = { ...newConv, messages: [] };
        activeDetailRef.current = targetConv;
        setConversations((prev) => [newConv, ...prev.filter((c) => c.id !== newConv.id)]);
        setActiveId(newConv.id);
        setActiveDetail(targetConv);
      } catch (err) {
        setErrorBanner(getErrorMessage(err, 'Failed to initialize conversation.'));
        setInputContent(content);
        return;
      }
    }

    // Optimistic user message
    const tempUserMsg: ConversationMessage = {
      id: -1,
      conversation_id: currentConvId,
      role: 'user',
      content,
      created_at: new Date(0).toISOString(),
    };

    const optimisticDetail: ConversationDetail = {
      ...targetConv,
      messages: [...targetConv.messages.filter((m) => m.id !== -1), tempUserMsg],
    };
    activeDetailRef.current = optimisticDetail;
    setActiveDetail(optimisticDetail);

    setIsSending(true);

    try {
      const result = await conversationService.sendMessage(currentConvId, { content });

      setActiveDetail((prev) => {
        const base = prev || targetConv;
        const filtered = base.messages.filter((m) => m.id !== tempUserMsg.id);
        const updated: ConversationDetail = {
          ...base,
          messages: [...filtered, result.user_message, result.assistant_message],
        };
        activeDetailRef.current = updated;
        return updated;
      });

      // Update title in sidebar list if changed
      const updatedList = await conversationService.listConversations();
      setConversations(updatedList);
    } catch (err) {
      setErrorBanner(getErrorMessage(err, 'Failed to send message to AI assistant.'));
      // Remove optimistic message on error and restore input text
      setActiveDetail((prev) => {
        if (!prev) return null;
        const cleaned: ConversationDetail = {
          ...prev,
          messages: prev.messages.filter((m) => m.id !== tempUserMsg.id),
        };
        activeDetailRef.current = cleaned;
        return cleaned;
      });
      setInputContent(content);
    } finally {
      setIsSending(false);
      setTimeout(() => textareaRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] max-w-7xl mx-auto w-full px-2 sm:px-4 lg:px-8 py-3">
        {/* Error notification banner */}
        {errorBanner && (
          <div className="mb-3 px-4 py-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-rose-700 dark:text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-semibold">Notice:</span>
              <span>{errorBanner}</span>
            </div>
            <button
              onClick={() => setErrorBanner(null)}
              className="text-rose-500 hover:text-rose-700 dark:hover:text-rose-200 font-bold ml-3"
            >
              ✕
            </button>
          </div>
        )}

        <div className="flex-1 flex overflow-hidden rounded-2xl border border-slate-200/90 dark:border-slate-800/80 bg-white dark:bg-slate-900 shadow-sm">
          {/* Mobile sidebar overlay toggle */}
          <div className="sm:hidden absolute top-20 right-6 z-30">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 text-xs shadow-xs"
            >
              {sidebarOpen ? 'Close History' : 'Chat History'}
            </button>
          </div>

          {/* Left Sidebar: Conversations History */}
          <aside
            className={`w-72 sm:w-80 border-r border-slate-200 dark:border-slate-800/80 flex flex-col bg-slate-50/70 dark:bg-slate-950/40 ${
              sidebarOpen
                ? 'absolute inset-y-16 left-0 z-40 w-4/5 max-w-xs shadow-xl bg-white dark:bg-slate-950'
                : 'hidden sm:flex'
            }`}
          >
            {/* Sidebar Header */}
            <div className="p-3.5 border-b border-slate-200/90 dark:border-slate-800/80 flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Conversations
              </h2>
              <button
                onClick={handleNewChat}
                type="button"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs transition-all hover:scale-[1.02]"
              >
                <span>+</span>
                <span>New Chat</span>
              </button>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {isLoadingList ? (
                <div className="p-4 text-center text-xs text-slate-400">
                  <div className="w-5 h-5 mx-auto mb-2 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                  Loading conversations...
                </div>
              ) : conversations.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-400 dark:text-slate-500">
                  <p>No conversations yet.</p>
                  <p className="mt-1">Click &quot;New Chat&quot; to begin discussing your learning roadmap.</p>
                </div>
              ) : (
                conversations.map((conv) => {
                  const isActive = conv.id === activeId;
                  return (
                    <div
                      key={conv.id}
                      onClick={() => {
                        setActiveId(conv.id);
                        setSidebarOpen(false);
                      }}
                      className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-colors text-xs ${
                        isActive
                          ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-900 dark:text-emerald-300 font-semibold border border-emerald-200/80 dark:border-emerald-500/20 shadow-xs'
                          : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                      }`}
                    >
                      <div className="flex items-center gap-2 truncate pr-2">
                        <span className="text-slate-400 group-hover:text-emerald-500">💬</span>
                        <span className="truncate">{conv.title}</span>
                      </div>
                      <button
                        onClick={(e) => handleDeleteConversation(conv.id, e)}
                        title="Delete conversation"
                        className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 transition-opacity"
                      >
                        🗑
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </aside>

          {/* Right Area: Active Chat Dialogue */}
          <main className="flex-1 flex flex-col overflow-hidden bg-white dark:bg-slate-900">
            {/* Chat Header */}
            <div className="h-14 px-4 sm:px-6 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between">
              <div className="flex items-center gap-2.5 truncate">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-xs shadow-emerald-500/50" />
                <h1 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {activeDetail?.title || 'Masar AI Assistant'}
                </h1>
              </div>
              <div className="hidden sm:flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono">
                  nemotron-3-ultra
                </span>
                <span>• Multi-Turn Context</span>
              </div>
            </div>

            {/* Message Thread Scroll Area */}
            <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
              {isLoadingDetail ? (
                <div className="flex items-center justify-center h-full text-xs text-slate-400">
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                    <span>Loading conversation history...</span>
                  </div>
                </div>
              ) : !activeDetail || activeDetail.messages.length === 0 ? (
                /* Empty state with prompt suggestion chips */
                <div className="flex flex-col items-center justify-center min-h-[50vh] text-center max-w-xl mx-auto space-y-6">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white text-xl shadow-md shadow-emerald-500/20">
                    ⚡
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                      How can Masar AI assist your learning today?
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
                      Discuss your software engineering goals, explore system concepts, draft roadmaps, or clarify architectural decisions.
                    </p>
                  </div>

                  {/* Suggestion Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
                    {PROMPT_SUGGESTIONS.map((item, idx) => (
                      <button
                        key={idx}
                        disabled={isSending}
                        onClick={() => handleSendMessage(item.prompt)}
                        className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-emerald-500/50 dark:hover:border-emerald-500/50 bg-slate-50/50 dark:bg-slate-950/40 hover:bg-emerald-50/30 dark:hover:bg-emerald-950/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-left group"
                      >
                        <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 group-hover:text-emerald-600 dark:group-hover:text-emerald-400">
                          {item.title} →
                        </h4>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                          {item.description}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                /* Dialogue Messages */
                activeDetail.messages.map((msg) => {
                  const isUser = msg.role === 'user';
                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto justify-end' : 'mr-auto justify-start'}`}
                    >
                      {!isUser && (
                        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold shadow-xs">
                          AI
                        </div>
                      )}

                      <div
                        className={`rounded-2xl px-4 py-3 text-xs leading-relaxed max-w-[85%] ${
                          isUser
                            ? 'bg-emerald-600 text-white shadow-xs font-medium'
                            : 'bg-slate-100 dark:bg-slate-800/80 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700/60 shadow-xs'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-4 mb-1 text-[10px] opacity-75">
                          <span className="font-semibold uppercase tracking-wider">
                            {isUser ? 'You' : 'Masar AI'}
                          </span>
                          <span>
                            {new Date(msg.created_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>
                        <div className="whitespace-pre-wrap select-text">{msg.content}</div>
                      </div>

                      {isUser && (
                        <div className="w-8 h-8 rounded-xl bg-slate-200 dark:bg-slate-700 flex-shrink-0 flex items-center justify-center text-slate-700 dark:text-slate-200 text-xs font-bold shadow-xs">
                          👤
                        </div>
                      )}
                    </div>
                  );
                })
              )}

              {/* Sending / Thinking Indicator */}
              {isSending && (
                <div className="flex gap-3 max-w-3xl mr-auto justify-start">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold animate-pulse">
                    AI
                  </div>
                  <div className="rounded-2xl px-4 py-3 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 text-xs flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                    <span>Generating architectural response...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Composer Footer */}
            <div className="p-3 sm:p-4 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/30">
              <div className="relative flex items-end gap-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 focus-within:border-emerald-500 dark:focus-within:border-emerald-500 transition-colors p-2 shadow-xs">
                <textarea
                  ref={textareaRef}
                  value={inputContent}
                  onChange={(e) => setInputContent(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask Masar AI about your learning goals or concepts (Enter to send, Shift+Enter for newline)..."
                  rows={2}
                  disabled={isSending}
                  className="flex-1 bg-transparent text-slate-900 dark:text-white placeholder-slate-400 text-xs resize-none focus:outline-none px-2 py-1 max-h-32"
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!inputContent.trim() || isSending}
                  type="button"
                  className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:hover:bg-emerald-600 text-white font-semibold text-xs transition-all shadow-xs flex items-center gap-1.5"
                >
                  {isSending ? (
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span>Send ↗</span>
                  )}
                </button>
              </div>
              <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
                <span>Shift + Enter for new line</span>
                <span>Powered by Nemotron-3 • OpenAI-compatible OpenRouter</span>
              </div>
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
