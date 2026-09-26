import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Bookmark, Loader2, Sparkles, Trash2 } from 'lucide-react';
import type { ChatMessage } from '../../types';

interface ChatSectionProps {
  messages: ChatMessage[];
  onSendMessage: (question: string) => void;
  isLoading: boolean;
  onNavigateToPage: (page: number, textSnippet?: string) => void;
  isDisabled: boolean;
  onClearChat: () => void;
}

export const ChatSection: React.FC<ChatSectionProps> = ({
  messages,
  onSendMessage,
  isLoading,
  onNavigateToPage,
  isDisabled,
  onClearChat,
}) => {
  const [inputQuestion, setInputQuestion] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputQuestion.trim() || isLoading || isDisabled) return;

    onSendMessage(inputQuestion.trim());
    setInputQuestion('');
  };

  const sampleQuestions = [
    "What is the notice period for termination?",
    "Is there any automatic renewal clause?",
    "What are my major financial obligations?",
    "What is the governing law and jurisdiction?"
  ];

  return (
    <div className="chat-section-card">
      <div className="chat-header">
        <div className="chat-title-group">
          <Bot size={18} className="chat-bot-icon" />
          <span>Document Chat Q&A</span>
        </div>
        {messages.length > 0 && (
          <button 
            onClick={onClearChat}
            className="btn-clear-chat" 
            title="Clear chat history"
          >
            <Trash2 size={14} /> Clear
          </button>
        )}
      </div>

      <div className="chat-history-container">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <Sparkles size={28} className="empty-sparkle-icon" />
            <p className="empty-title">Ask questions about the uploaded PDF</p>
            <p className="empty-sub">Answers are strictly grounded in document content with direct page references.</p>

            {!isDisabled && (
              <div className="suggested-questions">
                <span className="suggested-label">Sample queries to try:</span>
                {sampleQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    className="chip-suggestion"
                    onClick={() => onSendMessage(q)}
                  >
                    "{q}"
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`chat-bubble-row ${msg.sender === 'user' ? 'user-row' : 'ai-row'}`}>
              <div className="avatar">
                {msg.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
              </div>
              <div className="message-content">
                <div className="message-header-row">
                  <span className="sender-name">{msg.sender === 'user' ? 'You' : 'AI Legal Assistant'}</span>
                  <span className="timestamp">{msg.timestamp}</span>
                </div>
                <div className="message-body">{msg.text}</div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="chat-sources-group">
                    <span className="sources-label">Sources:</span>
                    {msg.sources.map((src, sIdx) => (
                      <button
                        key={sIdx}
                        className="btn-source-tag"
                        onClick={() => onNavigateToPage(src.page, src.snippet)}
                        title={`Click to jump to Page ${src.page} in PDF`}
                      >
                        <Bookmark size={12} />
                        <span>Page {src.page}{src.section ? ` • ${src.section}` : ''}</span>
                        <span className="view-link">View source</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="chat-bubble-row ai-row loading-row">
            <div className="avatar"><Bot size={14} /></div>
            <div className="message-content">
              <div className="ai-typing-indicator">
                <Loader2 size={16} className="spinner-icon" />
                <span>Searching document context & formatting answer...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          placeholder="Anything particular to check in the document?"
          disabled={isDisabled || isLoading}
          className="chat-text-input"
        />
        <button
          type="submit"
          disabled={isDisabled || isLoading || !inputQuestion.trim()}
          className="btn-send-chat"
          title="Send Question"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
