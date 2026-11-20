export type DocumentFileType = 'pdf' | 'text' | 'markdown';

export interface DocumentItem {
  id: number;
  user_id: number;
  filename: string;
  file_type: DocumentFileType;
  file_size_bytes: number;
  file_size_display?: string;
  summary?: string | null;
  created_at: string;
}

export interface DocumentDetail extends DocumentItem {
  extracted_text: string;
  char_count?: number;
}

export interface DocumentSummarizeResponse {
  id: number;
  filename: string;
  summary: string;
}
