import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorker from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import { 
  ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Maximize2, FileX, Loader2, Bookmark, RefreshCw
} from 'lucide-react';

// Configure PDF.js worker via bundled Vite URL
pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

interface PdfViewerProps {
  pdfUrl: string | null;
  targetPage: number;
  highlightText?: string;
  onPageChange?: (page: number) => void;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({
  pdfUrl,
  targetPage,
  highlightText,
  onPageChange,
}) => {
  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [numPages, setNumPages] = useState<number>(0);
  const [scale, setScale] = useState<number>(1.15);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reloadTrigger, setReloadTrigger] = useState<number>(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRefs = useRef<{ [key: number]: HTMLCanvasElement | null }>({});
  const renderTasksRef = useRef<{ [key: number]: any }>({});

  // Single Source of Truth Refs to prevent programmatic scroll feedback loops
  const isProgrammaticScrollRef = useRef<boolean>(false);
  const programmaticTimeoutRef = useRef<any>(null);
  const lastTargetPageRef = useRef<number | null>(null);
  const targetPageRef = useRef<number>(targetPage);

  useEffect(() => {
    targetPageRef.current = targetPage;
  }, [targetPage]);

  // 1. Fetch & Load PDF Document
  useEffect(() => {
    if (!pdfUrl) {
      lastTargetPageRef.current = null;
      const timer = setTimeout(() => {
        setPdfDoc(null);
        setNumPages(0);
        setCurrentPage(1);
        setLoadError(null);
      }, 0);
      return () => clearTimeout(timer);
    }

    let isMounted = true;

    const loadPdf = async () => {
      setLoading(true);
      setLoadError(null);
      try {
        const response = await fetch(pdfUrl);
        if (!response.ok) {
          throw new Error(`Failed to fetch PDF (${response.status} ${response.statusText})`);
        }
        const arrayBuffer = await response.arrayBuffer();
        
        if (!isMounted) return;

        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        const doc = await loadingTask.promise;

        if (!isMounted) return;

        setPdfDoc(doc);
        setNumPages(doc.numPages);
        setCurrentPage(targetPageRef.current || 1);
        setLoading(false);
      } catch (err: any) {
        console.error('Error loading PDF in viewer:', err);
        if (isMounted) {
          setLoadError(err.message || 'Failed to load PDF document.');
          setLoading(false);
        }
      }
    };

    loadPdf();

    return () => {
      isMounted = false;
    };
  }, [pdfUrl, reloadTrigger]);

  // 2. Programmatic Navigation to target page (Flicker-Free & Stable)
  useEffect(() => {
    if (targetPage > 0 && targetPage <= numPages) {
      // Avoid redundant scroll if targetPage hasn't changed
      if (lastTargetPageRef.current === targetPage) return;
      lastTargetPageRef.current = targetPage;

      setCurrentPage(targetPage);

      // Flag programmatic scrolling active to block scroll-event feedback
      isProgrammaticScrollRef.current = true;
      if (programmaticTimeoutRef.current) {
        clearTimeout(programmaticTimeoutRef.current);
      }

      const targetElement = document.getElementById(`pdf-page-${targetPage}`);
      if (targetElement && containerRef.current) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

      // Unlock scroll listener after smooth scroll finishes
      programmaticTimeoutRef.current = setTimeout(() => {
        isProgrammaticScrollRef.current = false;
      }, 800);
    }
  }, [targetPage, numPages]);

  // 3. Highlight target text on canvas
  const highlightTextOnCanvas = useCallback(async (
    page: pdfjsLib.PDFPageProxy,
    viewport: pdfjsLib.PageViewport,
    context: CanvasRenderingContext2D,
    searchTerm: string
  ) => {
    if (!searchTerm || !searchTerm.trim()) return;
    try {
      const textContent = await page.getTextContent();
      const termLower = searchTerm.toLowerCase();

      textContent.items.forEach((item: any) => {
        if (!item.str) return;
        const itemStrLower = item.str.toLowerCase();
        if (itemStrLower.includes(termLower) || termLower.includes(itemStrLower)) {
          const tx = pdfjsLib.Util.transform(viewport.transform, item.transform);
          const fontHeight = Math.sqrt(tx[2] * tx[2] + tx[3] * tx[3]);

          context.save();
          context.fillStyle = 'rgba(254, 240, 138, 0.55)'; // subtle translucent yellow
          context.strokeStyle = 'rgba(234, 179, 8, 0.85)';
          context.lineWidth = 1.5;
          context.fillRect(tx[4], tx[5] - fontHeight, item.width * viewport.scale, fontHeight * 1.2);
          context.strokeRect(tx[4], tx[5] - fontHeight, item.width * viewport.scale, fontHeight * 1.2);
          context.restore();
        }
      });
    } catch {
      // ignore highlight error
    }
  }, []);

  // 4. Render all page canvases (When document, page count, scale, or highlight changes)
  useEffect(() => {
    if (!pdfDoc || numPages === 0) return;

    let isMounted = true;

    // Cancel all previous render tasks
    Object.keys(renderTasksRef.current).forEach((pageNumStr) => {
      const pageNum = Number(pageNumStr);
      if (renderTasksRef.current[pageNum]) {
        try {
          renderTasksRef.current[pageNum].cancel();
        } catch {
          // ignore cancel error
        }
      }
    });
    renderTasksRef.current = {};

    const renderPage = async (pageNum: number) => {
      try {
        const page = await pdfDoc.getPage(pageNum);
        if (!isMounted) return;

        const canvas = canvasRefs.current[pageNum];
        if (!canvas) return;

        const context = canvas.getContext('2d');
        if (!context) return;

        const viewport = page.getViewport({ scale });
        
        // Handle HiDPI screens for sharp text rendering
        const dpr = window.devicePixelRatio || 1;
        canvas.width = viewport.width * dpr;
        canvas.height = viewport.height * dpr;
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;

        context.scale(dpr, dpr);

        const renderContext: any = {
          canvasContext: context,
          canvas: canvas,
          viewport: viewport,
        };

        const renderTask = page.render(renderContext);
        renderTasksRef.current[pageNum] = renderTask;

        await renderTask.promise;

        if (isMounted && highlightText && context) {
          highlightTextOnCanvas(page, viewport, context, highlightText);
        }
      } catch (err: any) {
        if (err.name !== 'RenderingCancelledException') {
          console.warn(`Error rendering page ${pageNum}:`, err);
        }
      }
    };

    // Render all pages
    for (let i = 1; i <= numPages; i++) {
      renderPage(i);
    }

    return () => {
      isMounted = false;
    };
  }, [pdfDoc, numPages, scale, highlightText, highlightTextOnCanvas]);

  // 5. User Manual Scroll Listener (Updates toolbar page counter without feedback loop)
  const handleScroll = () => {
    // Ignore scroll events triggered by programmatic navigation
    if (isProgrammaticScrollRef.current) return;
    if (!containerRef.current || numPages === 0) return;

    const containerTop = containerRef.current.getBoundingClientRect().top;

    let closestPage = 1;
    let minDistance = Infinity;

    for (let i = 1; i <= numPages; i++) {
      const el = document.getElementById(`pdf-page-${i}`);
      if (el) {
        const rect = el.getBoundingClientRect();
        const dist = Math.abs(rect.top - containerTop);
        if (dist < minDistance) {
          minDistance = dist;
          closestPage = i;
        }
      }
    }

    if (closestPage !== currentPage) {
      setCurrentPage(closestPage);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const p = currentPage - 1;
      setCurrentPage(p);
      lastTargetPageRef.current = p;
      isProgrammaticScrollRef.current = true;
      if (programmaticTimeoutRef.current) clearTimeout(programmaticTimeoutRef.current);

      const targetElement = document.getElementById(`pdf-page-${p}`);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

      programmaticTimeoutRef.current = setTimeout(() => {
        isProgrammaticScrollRef.current = false;
      }, 800);

      if (onPageChange) onPageChange(p);
    }
  };

  const handleNextPage = () => {
    if (currentPage < numPages) {
      const p = currentPage + 1;
      setCurrentPage(p);
      lastTargetPageRef.current = p;
      isProgrammaticScrollRef.current = true;
      if (programmaticTimeoutRef.current) clearTimeout(programmaticTimeoutRef.current);

      const targetElement = document.getElementById(`pdf-page-${p}`);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }

      programmaticTimeoutRef.current = setTimeout(() => {
        isProgrammaticScrollRef.current = false;
      }, 800);

      if (onPageChange) onPageChange(p);
    }
  };

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.15, 2.2));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.15, 0.5));
  const handleResetZoom = () => setScale(1.15);

  if (!pdfUrl) {
    return (
      <div className="pdf-viewer-empty">
        <div className="empty-viewer-icon-wrapper">
          <Bookmark size={40} className="empty-icon" />
        </div>
        <h3>Document Preview Workspace</h3>
        <p>Upload a PDF contract or agreement on the left panel to display the document and navigate findings.</p>
      </div>
    );
  }

  return (
    <div className="pdf-viewer-container">
      {/* SaaS Toolbar */}
      <div className="pdf-toolbar" role="toolbar" aria-label="PDF navigation and zoom controls">
        <div className="nav-controls">
          <button
            onClick={handlePrevPage}
            disabled={currentPage <= 1}
            className="btn-toolbar"
            aria-label="Go to previous page"
          >
            <ChevronLeft size={16} aria-hidden="true" />
          </button>
          <span className="page-indicator" aria-live="polite" aria-atomic="true">
            Page <strong className="current-page-num">{currentPage}</strong> of {numPages || 1}
          </span>
          <button
            onClick={handleNextPage}
            disabled={currentPage >= numPages}
            className="btn-toolbar"
            aria-label="Go to next page"
          >
            <ChevronRight size={16} aria-hidden="true" />
          </button>
        </div>

        <div className="zoom-controls">
          <button onClick={handleZoomOut} className="btn-toolbar" aria-label={`Zoom out (currently ${Math.round(scale * 100)}%)`}>
            <ZoomOut size={16} aria-hidden="true" />
          </button>
          <span className="zoom-level" aria-live="polite">{Math.round(scale * 100)}%</span>
          <button onClick={handleZoomIn} className="btn-toolbar" aria-label={`Zoom in (currently ${Math.round(scale * 100)}%)`}>
            <ZoomIn size={16} aria-hidden="true" />
          </button>
          <button onClick={handleResetZoom} className="btn-toolbar btn-reset-zoom" aria-label="Reset zoom to default (115%)">
            <Maximize2 size={15} aria-hidden="true" />
            <span>Fit</span>
          </button>
        </div>
      </div>

      {/* Vertical Scroll PDF Pages Container */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="pdf-pages-scroll-container"
        aria-label="PDF document pages"
      >
        {loading && (
          <div className="pdf-loading-overlay" role="status" aria-busy="true" aria-live="polite">
            <Loader2 size={32} className="spinner-icon" aria-hidden="true" />
            <span>Loading document pages...</span>
          </div>
        )}

        {loadError ? (
          <div className="pdf-error-overlay">
            <FileX size={36} className="error-icon" />
            <h4>Unable to preview PDF</h4>
            <p>{loadError}</p>
            <button 
              onClick={() => setReloadTrigger((prev) => prev + 1)}
              className="btn-retry-pdf"
            >
              <RefreshCw size={14} /> Retry Loading
            </button>
          </div>
        ) : (
          <div className="pdf-pages-list">
            {Array.from({ length: numPages }, (_, idx) => idx + 1).map((pageNum) => {
              const isTarget = pageNum === targetPage;
              return (
            <div
                  key={pageNum}
                  id={`pdf-page-${pageNum}`}
                  className={`pdf-page-wrapper ${isTarget ? 'target-highlighted-page' : ''}`}
                >
                  <div className="page-header-ribbon" aria-hidden="true">
                    <span className="page-num-label">Page {pageNum}</span>
                    {isTarget && (
                      <span className="target-finding-badge">
                        <Bookmark size={12} aria-hidden="true" />
                        Referenced Finding Location
                      </span>
                    )}
                  </div>
                  <div className="canvas-wrapper">
                    <canvas
                      ref={(el) => { canvasRefs.current[pageNum] = el; }}
                      className="pdf-page-canvas"
                      role="img"
                      aria-label={`PDF page ${pageNum} of ${numPages}`}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
