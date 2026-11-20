'use client';

import React, { useEffect, useRef, useState } from 'react';
import { DocumentDetail, DocumentItem } from '@/types/document';
import { documentService } from '@/services/api/documents';
import { ApiError } from '@/services/api/errors';

interface DocumentManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeDocumentId: number | null;
  onSelectDocument: (doc: DocumentItem | null) => void;
  onAttachAndPlan?: (doc: DocumentItem) => void;
}

export function DocumentManagerModal({
  isOpen,
  onClose,
  activeDocumentId,
  onSelectDocument,
  onAttachAndPlan,
}: DocumentManagerModalProps) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [summarizingId, setSummarizingId] = useState<number | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<DocumentDetail | null>(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    let isMounted = true;

    void (async () => {
      try {
        setIsLoading(true);
        const docs = await documentService.listDocuments();
        if (isMounted) {
          setDocuments(docs);
        }
      } catch (err) {
        if (isMounted) {
          if (err instanceof ApiError) {
            setErrorMsg(err.detail || err.message);
          } else if (err instanceof Error) {
            setErrorMsg(err.message);
          } else {
            setErrorMsg('Failed to load documents.');
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    })();

    return () => {
      isMounted = false;
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleFileUpload = async (file: File) => {
    // Validate file type
    const lowerName = file.name.toLowerCase();
    const isValidExt =
      lowerName.endsWith('.pdf') || lowerName.endsWith('.txt') || lowerName.endsWith('.md');
    if (!isValidExt) {
      setErrorMsg('Unsupported file format. Please upload PDF (.pdf), Text (.txt), or Markdown (.md).');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg('File exceeds 10 MB maximum upload limit.');
      return;
    }

    try {
      setIsUploading(true);
      setErrorMsg(null);
      const uploaded = await documentService.uploadDocument(file);
      setDocuments((prev) => [uploaded, ...prev]);
      onSelectDocument(uploaded);
    } catch (err) {
      if (err instanceof ApiError) {
        setErrorMsg(err.detail || err.message);
      } else if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Failed to upload document.');
      }
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      setErrorMsg(null);
      await documentService.deleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      if (activeDocumentId === docId) {
        onSelectDocument(null);
      }
      if (selectedDetail?.id === docId) {
        setSelectedDetail(null);
      }
    } catch {
      setErrorMsg('Failed to delete document.');
    }
  };

  const handleSummarize = async (doc: DocumentItem) => {
    try {
      setSummarizingId(doc.id);
      setErrorMsg(null);
      const result = await documentService.summarizeDocument(doc.id);
      setDocuments((prev) =>
        prev.map((d) => (d.id === doc.id ? { ...d, summary: result.summary } : d))
      );
      if (selectedDetail && selectedDetail.id === doc.id) {
        setSelectedDetail({ ...selectedDetail, summary: result.summary });
      }
    } catch {
      setErrorMsg('Failed to generate AI summary.');
    } finally {
      setSummarizingId(null);
    }
  };

  const handleViewDetail = async (doc: DocumentItem) => {
    try {
      setIsLoadingDetail(true);
      setErrorMsg(null);
      const detail = await documentService.getDocument(doc.id);
      setSelectedDetail(detail);
    } catch {
      setErrorMsg('Failed to load document content.');
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const getFileBadge = (type: string) => {
    switch (type) {
      case 'pdf':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800/60">
            PDF
          </span>
        );
      case 'markdown':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/60">
            MD
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/60">
            TXT
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">📁</span>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
                Learning Documents & Context
              </h2>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Upload resumes, syllabus, or technical materials to attach to your AI mentor chats
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Error notification */}
        {errorMsg && (
          <div className="mx-5 mt-3 px-3.5 py-2 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center justify-between">
            <span>{errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="text-rose-500 hover:underline text-[11px]">
              Dismiss
            </button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* Upload Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-5 text-center transition-all ${
              dragActive
                ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20'
                : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-950/40'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
              className="hidden"
            />
            <div className="flex flex-col items-center justify-center gap-1.5">
              <span className="text-2xl">📤</span>
              <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                Drag and drop your document here, or{' '}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                  className="text-emerald-600 dark:text-emerald-400 hover:underline font-bold"
                >
                  browse file
                </button>
              </p>
              <p className="text-[11px] text-slate-400">
                Supports PDF, Markdown (.md), and Plain Text (.txt) up to 10 MB
              </p>
              {isUploading && (
                <div className="mt-2 flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                  <div className="w-3.5 h-3.5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                  <span>Extracting document text & processing...</span>
                </div>
              )}
            </div>
          </div>

          {/* Document Detail Preview Drawer */}
          {selectedDetail && (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/60 p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-2">
                <div className="flex items-center gap-2">
                  {getFileBadge(selectedDetail.file_type)}
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                    {selectedDetail.filename}
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    ({selectedDetail.file_size_display || `${(selectedDetail.file_size_bytes / 1024).toFixed(1)} KB`})
                  </span>
                </div>
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  Close Preview ✕
                </button>
              </div>

              {selectedDetail.summary && (
                <div className="p-3 rounded-lg bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200/60 dark:border-emerald-800/40">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300 mb-1 flex items-center gap-1">
                    <span>✨ AI Technical Summary</span>
                  </div>
                  <div className="text-xs text-slate-700 dark:text-slate-200 whitespace-pre-wrap leading-relaxed">
                    {selectedDetail.summary}
                  </div>
                </div>
              )}

              <div>
                <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1 flex items-center justify-between">
                  <span>Extracted Text Content</span>
                  <span>{selectedDetail.char_count || selectedDetail.extracted_text.length} characters</span>
                </div>
                <div className="max-h-48 overflow-y-auto p-3 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-700 dark:text-slate-300 whitespace-pre-wrap select-text leading-relaxed">
                  {selectedDetail.extracted_text}
                </div>
              </div>
            </div>
          )}

          {/* Uploaded Documents List */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
              Your Library ({documents.length})
            </h3>

            {isLoading ? (
              <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                <span>Loading your documents...</span>
              </div>
            ) : documents.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
                No documents uploaded yet. Upload a syllabus or resume above.
              </div>
            ) : (
              <div className="space-y-2">
                {documents.map((doc) => {
                  const isActive = activeDocumentId === doc.id;
                  const isSummarizing = summarizingId === doc.id;

                  return (
                    <div
                      key={doc.id}
                      className={`p-3 rounded-xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                        isActive
                          ? 'border-emerald-500/80 bg-emerald-50/30 dark:bg-emerald-950/20 shadow-xs'
                          : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-start gap-3 min-w-0 flex-1">
                        <div className="pt-0.5">{getFileBadge(doc.file_type)}</div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold text-slate-900 dark:text-white truncate">
                              {doc.filename}
                            </span>
                            {isActive && (
                              <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-emerald-500 text-white">
                                ACTIVE IN CHAT
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                            <span>
                              {doc.file_size_display || `${(doc.file_size_bytes / 1024).toFixed(1)} KB`}
                            </span>
                            <span>•</span>
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                            {doc.summary && (
                              <>
                                <span>•</span>
                                <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                                  ✓ Summarized
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex flex-wrap items-center gap-1.5 sm:self-center">
                        <button
                          type="button"
                          onClick={() => handleViewDetail(doc)}
                          disabled={isLoadingDetail}
                          className="px-2.5 py-1 rounded-lg text-[11px] font-medium border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors"
                        >
                          Preview
                        </button>

                        <button
                          type="button"
                          onClick={() => handleSummarize(doc)}
                          disabled={isSummarizing}
                          className="px-2.5 py-1 rounded-lg text-[11px] font-medium border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1"
                        >
                          {isSummarizing ? (
                            <div className="w-3 h-3 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <span>✨ {doc.summary ? 'Re-summarize' : 'Summarize'}</span>
                          )}
                        </button>

                        {onAttachAndPlan && (
                          <button
                            type="button"
                            onClick={() => {
                              onSelectDocument(doc);
                              onAttachAndPlan(doc);
                              onClose();
                            }}
                            className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/80 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 transition-colors"
                          >
                            Plan Roadmap ↗
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() => {
                            if (isActive) {
                              onSelectDocument(null);
                            } else {
                              onSelectDocument(doc);
                              onClose();
                            }
                          }}
                          className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-colors ${
                            isActive
                              ? 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-slate-700'
                              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-xs'
                          }`}
                        >
                          {isActive ? 'Detach' : 'Attach'}
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDelete(doc.id)}
                          className="p-1 rounded-lg text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors text-xs"
                          title="Delete document"
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/40 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            {activeDocumentId ? '✓ Document active in current chat context' : 'No document attached'}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
