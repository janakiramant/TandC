import type { UploadResponse, ChatSource } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function uploadPdfDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(errData.detail || `Upload failed with status ${response.status}`);
  }

  return response.json();
}

export async function sendChatMessage(docId: string, question: string): Promise<{ answer: string; sources: ChatSource[]; is_grounded: boolean }> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      doc_id: docId,
      question: question,
    }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: 'Chat request failed' }));
    throw new Error(errData.detail || `Chat request failed with status ${response.status}`);
  }

  return response.json();
}

export function getPdfFileUrl(docId: string): string {
  return `${API_BASE_URL}/document/${docId}/file`;
}

export async function clearDocumentSession(docId: string): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/document/${docId}`, { method: 'DELETE' });
  } catch (e) {
    console.warn('Failed to clear session on backend', e);
  }
}
