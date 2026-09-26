export type FindingType = 'favorable' | 'risk' | 'important';

export interface Finding {
  id: string;
  type: FindingType;
  title: string;
  summary: string;
  page: number;
  section?: string;
  source_text: string;
}

export interface DocumentAnalysis {
  doc_id: string;
  filename: string;
  total_pages: number;
  summary: string;
  findings: Finding[];
  created_at: string;
  has_readable_text: boolean;
  error_message?: string;
}

export interface UploadResponse {
  doc_id: string;
  filename: string;
  total_pages: number;
  has_readable_text: boolean;
  message: string;
  analysis?: DocumentAnalysis;
}

export interface ChatSource {
  page: number;
  section?: string;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  sources?: ChatSource[];
  timestamp: string;
  is_grounded?: boolean;
}
