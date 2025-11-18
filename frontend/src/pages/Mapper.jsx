import React, { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import api from '../services/api'

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

export default function Mapper() {
  const [fileId, setFileId] = useState(null)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [outputPdfId, setOutputPdfId] = useState(null)
  const [conference, setConference] = useState('IEEE')
  const [columns2, setColumns2] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [scale, setScale] = useState(1.0)

  const handleUpload = async (e) => {
    setError(null)
    const f = e.target.files[0]
    if (!f) return
    setLoading(true)
    try {
      const res = await api.uploadFile(f)
      setFileId(res.file_id)
      setOutputPdfId(res.file_id)
      setPdfUrl(api.getFileUrl(res.file_id))
    } catch (err) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleMap = async () => {
    if (!fileId) return setError('Upload a file first')
    setLoading(true)
    setError(null)
    try {
      const resp = await api.fixLatexRag({
        file_id: fileId,
        document_type: 'research',
        conference,
        column_format: columns2 ? '2-column' : '1-column',
        converted: true,
        original_format: 'PDF',
        compile_pdf: true
      })

      if (resp?.file_id) {
        setFileId(resp.file_id)
      }

      const pdfId = resp?.pdf_id || resp?.file_id
      if (pdfId) {
        setOutputPdfId(pdfId)
        setPdfUrl(api.getFileUrl(pdfId))
      }
    } catch (err) {
      setError(err.message || 'Processing failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    const pdfId = pdfUrl ? pdfUrl.split('/').pop() : outputPdfId || fileId
    if (!pdfId) return setError('No processed file to download')
    setLoading(true)
    try {
      await api.downloadFile(pdfId)
    } catch (err) {
      setError(err.message || 'Download failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-800 flex items-center gap-3 mb-2">
            <span>📐</span> Format Mapper
          </h1>
          <p className="text-slate-600 text-sm">Convert PDF to research paper format with conference-specific styling</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white shadow-sm border border-slate-200 rounded-lg p-6">
          <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
            <span>📤</span> Upload PDF Document
          </h2>
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-400 transition">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleUpload}
              disabled={loading}
              className="block mx-auto cursor-pointer"
            />
            <p className="text-sm text-slate-500 mt-2">Drag and drop or click to select your PDF file</p>
          </div>
          
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
              ⚠️ {error}
            </div>
          )}
          
          {loading && (
            <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg text-blue-700 text-sm">
              ⏳ Processing document...
            </div>
          )}
        </div>

        {/* Configuration and Preview Section */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Configuration Panel */}
          <div className="bg-white border border-slate-200 p-6 rounded-lg space-y-5">
            <h2 className="font-semibold text-slate-700 flex items-center gap-2">
              <span>⚙️</span> Format Options
            </h2>

            {/* Conference Selection */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                <span>🏢</span> Conference Format
              </label>
              <select 
                value={conference} 
                onChange={(e) => setConference(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200 transition"
              >
                <option value="IEEE">📡 IEEE</option>
                <option value="ACM">💻 ACM</option>
                <option value="SPRINGER">📖 Springer</option>
                <option value="ELSEVIER">🔬 Elsevier</option>
                <option value="GENERIC">🔷 Generic</option>
              </select>
            </div>

            {/* Column Format Selection */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                <span>📊</span> Column Format
              </label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="radio"
                    name="columns"
                    checked={!columns2}
                    onChange={() => setColumns2(false)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">1️⃣ Single Column</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="radio"
                    name="columns"
                    checked={columns2}
                    onChange={() => setColumns2(true)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">2️⃣ Two Column</span>
                </label>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button 
                className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition flex items-center justify-center gap-2"
                onClick={handleMap} 
                disabled={loading || !fileId}
              >
                {loading ? '⏳ Processing...' : '🔧 Apply Format'}
              </button>
              <button 
                className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-semibold transition flex items-center justify-center gap-2"
                onClick={handleDownload} 
                disabled={loading || !outputPdfId}
              >
                📥 Download PDF
              </button>
            </div>
          </div>

          {/* PDF Preview */}
          <div className="bg-white border border-slate-200 p-6 rounded-lg space-y-4">
            <h2 className="font-semibold text-slate-700 flex items-center gap-2">
              <span>👁️</span> Document Preview
            </h2>
            
            {pdfUrl ? (
              <div className="border border-slate-300 rounded-lg overflow-hidden">
                <div className="flex justify-between items-center p-3 bg-slate-50 border-b">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage <= 1}
                      className="px-3 py-2 border border-slate-300 rounded hover:bg-slate-100 disabled:opacity-50 text-sm font-medium transition"
                    >
                      ⬅️ Prev
                    </button>
                    <span className="text-sm font-medium text-slate-700 min-w-fit">
                      Page {currentPage} / {numPages || '—'}
                    </span>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(numPages || 1, p + 1))}
                      disabled={currentPage >= (numPages || 1)}
                      className="px-3 py-2 border border-slate-300 rounded hover:bg-slate-100 disabled:opacity-50 text-sm font-medium transition"
                    >
                      Next ➡️
                    </button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setScale(s => Math.max(0.5, s - 0.1))}
                      className="px-2 py-2 border border-slate-300 rounded hover:bg-slate-100 text-sm transition"
                      title="Zoom out"
                    >
                      🔍−
                    </button>
                    <span className="text-sm font-medium text-slate-700 min-w-fit">{Math.round(scale * 100)}%</span>
                    <button
                      onClick={() => setScale(s => Math.min(2.0, s + 0.1))}
                      className="px-2 py-2 border border-slate-300 rounded hover:bg-slate-100 text-sm transition"
                      title="Zoom in"
                    >
                      🔍+
                    </button>
                  </div>
                </div>
                
                <div 
                  className="overflow-auto max-h-[600px] cursor-move relative scroll-smooth"
                  style={{ 
                    backgroundColor: '#f0f0f0',
                    padding: '20px',
                    userSelect: 'none'
                  }}
                  onScroll={(e) => {
                    const container = e.currentTarget;
                    const scrollPos = container.scrollTop;
                    const pageHeight = container.scrollHeight / (numPages || 1);
                    const newPage = Math.floor(scrollPos / pageHeight) + 1;
                    if (newPage !== currentPage && newPage > 0 && newPage <= numPages) {
                      setCurrentPage(newPage);
                    }
                  }}
                  onMouseDown={(e) => {
                    const ele = e.currentTarget;
                    const startX = e.pageX - ele.offsetLeft;
                    const startY = e.pageY - ele.offsetTop;
                    const startScrollLeft = ele.scrollLeft;
                    const startScrollTop = ele.scrollTop;

                    const handleMouseMove = (e) => {
                      e.preventDefault();
                      const x = e.pageX - ele.offsetLeft;
                      const y = e.pageY - ele.offsetTop;
                      const walkX = (x - startX) * 1.5;
                      const walkY = (y - startY) * 1.5;
                      ele.scrollLeft = startScrollLeft - walkX;
                      ele.scrollTop = startScrollTop - walkY;
                    };

                    const handleMouseUp = () => {
                      document.removeEventListener('mousemove', handleMouseMove);
                      document.removeEventListener('mouseup', handleMouseUp);
                    };

                    document.addEventListener('mousemove', handleMouseMove);
                    document.addEventListener('mouseup', handleMouseUp);
                  }}
                >
                  <div className="inline-block min-w-full min-h-full space-y-8">
                    <Document
                      file={pdfUrl}
                      onLoadSuccess={({ numPages }) => {
                        setNumPages(numPages)
                        setCurrentPage(1)
                      }}
                    >
                      {Array.from(new Array(numPages || 0), (_, index) => (
                        <div key={`page_${index + 1}`} className="relative">
                          <div className="absolute -left-10 top-0 bg-blue-600 text-white px-2 py-1 rounded-l text-xs font-bold">
                            {index + 1}
                          </div>
                          <Page
                            pageNumber={index + 1}
                            scale={scale}
                            renderAnnotationLayer={false}
                            renderTextLayer={false}
                          />
                        </div>
                      ))}
                    </Document>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 bg-slate-50 rounded border border-dashed border-slate-300 text-slate-500">
                <div className="text-center">
                  <p className="text-sm">📄 No preview available</p>
                  <p className="text-xs text-slate-400 mt-1">Upload a PDF to see preview</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
