import React, { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import api from '../services/api'

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

export default function Editor() {
  const [fileId, setFileId] = useState(null)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [outputPdfId, setOutputPdfId] = useState(null)
  const [documentType, setDocumentType] = useState('normal')
  const [conference, setConference] = useState('GENERIC')
  const [columnFormat, setColumnFormat] = useState('1-column')
  const [editMode, setEditMode] = useState('single') // 'single' or 'batch'
  const [prompt, setPrompt] = useState('')
  const [batchPrompts, setBatchPrompts] = useState([''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [numPages, setNumPages] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [scale, setScale] = useState(1.0)
  const [isProcessed, setIsProcessed] = useState(false) // Track if PDF has been processed

  const handleUpload = async (e) => {
    setError(null)
    const f = e.target.files[0]
    if (!f) return
    
    // Validate file type
    if (!f.type.includes('pdf') && !f.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a valid PDF file')
      return
    }

    setLoading(true)
    try {
      // First, check if the file is readable
      const fileReader = new FileReader()
      
      const readFile = new Promise((resolve, reject) => {
        fileReader.onload = () => resolve()
        fileReader.onerror = () => reject(new Error('File is corrupted or unreadable'))
        fileReader.readAsArrayBuffer(f)
      })

      await readFile

      const res = await api.uploadFile(f)
      setFileId(res.file_id)
      setOutputPdfId(res.file_id)
      setPdfUrl(api.getFileUrl(res.file_id))

      // Verify the uploaded file is accessible
      const checkFile = await fetch(api.getFileUrl(res.file_id))
      if (!checkFile.ok) {
        throw new Error('Uploaded file verification failed')
      }

    } catch (err) {
      console.error('Upload error:', err)
      setError(err.message || 'Upload failed. Please ensure the file is a valid PDF')
    } finally {
      setLoading(false)
    }
  }

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages)
    setCurrentPage(1)
  }

  const changePage = (offset) => {
    setCurrentPage(prevPage => {
      const newPage = prevPage + offset
      return Math.min(Math.max(1, newPage), numPages || 1)
    })
  }

  const zoomIn = () => setScale(s => Math.min(s + 0.1, 2.0))
  const zoomOut = () => setScale(s => Math.max(s - 0.1, 0.5))

  const handleProcessPDF = async () => {
    if (!fileId) return setError('Upload a file first')
    setError(null)
    setLoading(true)
    try {
      // Process the PDF with RAG fixer using selected options
      const fixResp = await api.fixLatexRag({
        file_id: fileId,
        document_type: documentType,
        conference: conference,
        column_format: columnFormat,
        converted: true,
        original_format: 'PDF',
        compile_pdf: false
      })

      if (!fixResp?.file_id) {
        throw new Error('Failed to process PDF. Please try again.')
      }

      // Update file ID with the processed version
      setFileId(fixResp.file_id)
      setOutputPdfId(fixResp.file_id)
      
      // Try to compile to show result
      const compileResp = await api.compilePdf({
        file_id: fixResp.file_id,
        engine: 'xelatex'
      })

      if (compileResp?.pdf_id) {
        setOutputPdfId(compileResp.pdf_id)
        setPdfUrl(api.getFileUrl(compileResp.pdf_id))
      }

      setIsProcessed(true)
      setError(`✅ PDF processed successfully! Issues found: ${fixResp.report?.total_issues || 0}`)
    } catch (err) {
      console.error('Process error:', err)
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error || 
        err.message || 
        'Failed to process PDF. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitPrompt = async () => {
    if (!fileId) return setError('Upload a file first')
    
    if (editMode === 'batch') {
      return handleBatchSubmit()
    }
    
    if (!prompt.trim()) return setError('Please enter an editing prompt')
    setError(null)
    setLoading(true)
    try {
      // First verify the file is still accessible
      try {
        const checkFile = await fetch(api.getFileUrl(fileId))
        if (!checkFile.ok) {
          throw new Error('Source file is no longer accessible. Please upload again.')
        }
      } catch (err) {
        throw new Error('Unable to access the source file. Please upload again.')
      }

      // Step 1: Fix LaTeX (RAG) to prepare editable source
      let preparedFileId = fileId
      try {
        const fixResp = await api.fixLatexRag({
          file_id: fileId,
          document_type: documentType,
          conference: conference,
          column_format: columnFormat,
          converted: true,
          original_format: 'PDF',
          compile_pdf: false
        })

        if (!fixResp?.file_id) {
          throw new Error('RAG fix did not return an editable file.')
        }

        preparedFileId = fixResp.file_id
        setFileId(fixResp.file_id)
      } catch (err) {
        throw new Error(err.message || 'Unable to prepare the document for editing. Please retry the format mapping step.')
      }

      // Step 2: Apply edit prompt
      const editResp = await api.editDocument({
        file_id: preparedFileId,
        prompt: prompt.trim(),
        compile_pdf: false
      })

      if (!editResp?.file_id) {
        throw new Error(editResp?.message || 'Edit operation did not return an updated file')
      }

      // Step 3: Compile updated LaTeX into PDF
      const compileResp = await api.compilePdf({
        file_id: editResp.file_id,
        engine: 'xelatex'
      })

      const compiledPdfId = compileResp?.pdf_id || compileResp?.file_id
      if (!compiledPdfId) {
        throw new Error('No PDF generated after compilation')
      }

      // Update UI with the newly compiled PDF
      setFileId(editResp.file_id)
      setOutputPdfId(compiledPdfId)
      setPdfUrl(api.getFileUrl(compiledPdfId))
      setPrompt('')
    } catch (err) {
      console.error('Edit error:', err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error || 
        err.message || 
        'Editing failed. Please ensure the document is in a valid format.'
      );
    } finally {
      setLoading(false)
    }
  }

  const handleBatchSubmit = async () => {
    const validPrompts = batchPrompts.filter(p => p.trim())
    if (validPrompts.length === 0) return setError('Please enter at least one editing prompt')
    setError(null)
    setLoading(true)
    try {
      // Step 1: Fix LaTeX (RAG) to prepare editable source
      let preparedFileId = fileId
      try {
        const fixResp = await api.fixLatexRag({
          file_id: fileId,
          document_type: documentType,
          conference: conference,
          column_format: columnFormat,
          converted: true,
          original_format: 'PDF',
          compile_pdf: false
        })

        if (!fixResp?.file_id) {
          throw new Error('RAG fix did not return an editable file.')
        }

        preparedFileId = fixResp.file_id
        setFileId(fixResp.file_id)
      } catch (err) {
        throw new Error(err.message || 'Unable to prepare the document for editing.')
      }

      // Step 2: Apply batch edits
      const batchResp = await api.batchEditDocument({
        file_id: preparedFileId,
        queries: validPrompts,
        compile_pdf: false,
        delay: 1.5
      })

      if (!batchResp?.file_id) {
        throw new Error(batchResp?.message || 'Batch edit operation did not return an updated file')
      }

      // Step 3: Compile updated LaTeX into PDF
      const compileResp = await api.compilePdf({
        file_id: batchResp.file_id,
        engine: 'xelatex'
      })

      const compiledPdfId = compileResp?.pdf_id || compileResp?.file_id
      if (!compiledPdfId) {
        throw new Error('No PDF generated after compilation')
      }

      // Update UI with the newly compiled PDF
      setFileId(batchResp.file_id)
      setOutputPdfId(compiledPdfId)
      setPdfUrl(api.getFileUrl(compiledPdfId))
      setBatchPrompts([''])
      setError(`✅ Batch edit completed: ${batchResp.successful_operations}/${batchResp.total_operations} operations successful`)
    } catch (err) {
      console.error('Batch edit error:', err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.error || 
        err.message || 
        'Batch editing failed. Please ensure the document is in a valid format.'
      );
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    const currentPdfId = pdfUrl ? pdfUrl.split('/').pop() : outputPdfId || fileId
    if (!currentPdfId) return setError('No file to download')
    setLoading(true)
    try {
      await api.downloadFile(currentPdfId)
    } catch (err) {
      setError(err.message || 'Download failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-700">🤖 AI Document Editor</h1>

      {/* Upload Section */}
      <div className="bg-white shadow-sm border rounded p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-lg">📤</span>
          <label className="block text-sm font-semibold text-slate-700">Upload PDF File</label>
        </div>
        <input type="file" accept=".pdf" onChange={handleUpload} className="border rounded px-3 py-2 w-full" />
        {loading && <div className="mt-2 text-sm text-blue-600">⏳ Processing...</div>}
        {error && <div className="mt-2 text-sm text-red-600">❌ {error}</div>}
        
        {/* Document Configuration Section - Only show before processing */}
        {fileId && !isProcessed && (
          <div className="mt-6 pt-6 border-t space-y-6">
            <h3 className="font-semibold text-slate-700 flex items-center gap-2">
              <span>⚙️</span> PDF Processing Options
            </h3>
            
            <div className="grid md:grid-cols-3 gap-4">
              {/* Document Type Selection */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                  <span>📄</span> Document Type
                </label>
                <select 
                  value={documentType}
                  onChange={(e) => {
                    setDocumentType(e.target.value)
                    // Reset to defaults when switching types
                    if (e.target.value === 'normal') {
                      setConference('GENERIC')
                      setColumnFormat('1-column')
                    } else {
                      setConference('IEEE')
                      setColumnFormat('2-column')
                    }
                  }}
                  className="w-full border rounded px-3 py-2 text-sm bg-white hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
                >
                  <option value="normal">📋 Normal Document</option>
                  <option value="research">📚 Research Paper</option>
                </select>
              </div>
              
              {/* Conference Selection - Only for Research Papers */}
              {documentType === 'research' && (
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                    <span>🏢</span> Conference Format
                  </label>
                  <select 
                    value={conference}
                    onChange={(e) => setConference(e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm bg-white hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  >
                    <option value="IEEE">📡 IEEE</option>
                    <option value="ACM">💻 ACM</option>
                    <option value="SPRINGER">📖 Springer</option>
                    <option value="ELSEVIER">🔬 Elsevier</option>
                    <option value="GENERIC">🔷 Generic</option>
                  </select>
                </div>
              )}
              
              {/* Column Format Selection - Only for Research Papers */}
              {documentType === 'research' && (
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 flex items-center gap-2">
                    <span>📊</span> Column Format
                  </label>
                  <select 
                    value={columnFormat}
                    onChange={(e) => setColumnFormat(e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm bg-white hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  >
                    <option value="1-column">1️⃣ Single Column</option>
                    <option value="2-column">2️⃣ Two Column</option>
                  </select>
                </div>
              )}
            </div>

            {/* Process PDF Button */}
            <div className="flex gap-3 pt-4">
              <button 
                className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition flex items-center justify-center gap-2"
                onClick={handleProcessPDF} 
                disabled={loading}
              >
                {loading ? '⏳ Processing PDF...' : '🔧 Process PDF'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Preview and Editing Section */}
      {/* Preview and Editing Section - Only show after processing */}
      {isProcessed && pdfUrl && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* PDF Preview */}
          <div className="bg-white border p-4 rounded">
            <h2 className="font-semibold mb-3 flex items-center gap-2">
              <span>👁️</span> Processed Document Preview
            </h2>
            <div className="border rounded p-2">
              {pdfUrl && (
                <>
                  <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => changePage(-1)}
                        disabled={currentPage <= 1}
                        className="px-2 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 text-sm"
                      >
                        ⬅️ Prev
                      </button>
                      <span className="text-sm font-medium">
                        {currentPage} / {numPages || '—'}
                      </span>
                      <button
                        onClick={() => changePage(1)}
                        disabled={currentPage >= (numPages || 1)}
                        className="px-2 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 text-sm"
                      >
                        Next ➡️
                      </button>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={zoomOut}
                        className="px-2 py-1 border rounded hover:bg-gray-100 text-sm"
                        title="Zoom out"
                      >
                        🔍−
                      </button>
                      <span className="text-sm font-medium">{Math.round(scale * 100)}%</span>
                      <button
                        onClick={zoomIn}
                        className="px-2 py-1 border rounded hover:bg-gray-100 text-sm"
                        title="Zoom in"
                      >
                        🔍+
                      </button>
                    </div>
                  </div>
                  <div 
                    className="overflow-auto max-h-[800px] cursor-move relative scroll-smooth"
                    style={{ 
                      backgroundColor: '#f0f0f0',
                      padding: '20px',
                      userSelect: 'none'
                    }}
                  >
                    <div className="inline-block min-w-full min-h-full space-y-8">
                      <Document file={pdfUrl} onLoadSuccess={onDocumentLoadSuccess}>
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
                </>
              )}
            </div>
            <div className="mt-4">
              <button 
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
                onClick={handleDownload} 
                disabled={loading}
              >
                📥 Download PDF
              </button>
            </div>
          </div>

          {/* Editing Panel */}
          <div className="bg-white border p-4 rounded space-y-4">
            <h2 className="font-semibold flex items-center gap-2">
              <span>✏️</span> Edit Document
            </h2>

            {/* Edit Mode Selection */}
            <div className="space-y-3 pb-4 border-b">
              <h3 className="font-semibold text-slate-700 flex items-center gap-2 text-sm">
                <span>⚙️</span> Edit Mode
              </h3>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="editMode"
                    value="single"
                    checked={editMode === 'single'}
                    onChange={(e) => setEditMode(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">🔹 Single Operation</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="editMode"
                    value="batch"
                    checked={editMode === 'batch'}
                    onChange={(e) => setEditMode(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-slate-700">⚡ Batch Operations</span>
                </label>
              </div>
            </div>
            
            {editMode === 'single' ? (
              <>
                <textarea
                  className="w-full border rounded p-2 h-40 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-200"
                  placeholder="Enter editing instruction&#10;Example: 'replace accuracy with precision'&#10;Example: 'make conclusion bold'&#10;Example: 'remove all references to COVID'"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={loading}
                />
                <button
                  className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50 font-medium"
                  onClick={handleSubmitPrompt}
                  disabled={loading || !prompt.trim()}
                >
                  {loading ? '⏳ Processing...' : '✅ Apply Edit'}
                </button>
              </>
            ) : (
              <>
                <div className="space-y-3">
                  {batchPrompts.map((p, idx) => (
                    <div key={idx} className="space-y-2 p-3 bg-slate-50 rounded border border-slate-200">
                      <div className="flex justify-between items-center">
                        <label className="text-sm font-medium text-slate-700">Operation {idx + 1}</label>
                        <button
                          onClick={() => {
                            const newPrompts = batchPrompts.filter((_, i) => i !== idx);
                            setBatchPrompts(newPrompts);
                          }}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          ❌ Remove
                        </button>
                      </div>
                      <textarea
                        className="w-full border rounded p-2 h-20 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-200"
                        placeholder={`Edit instruction ${idx + 1}...`}
                        value={p}
                        onChange={(e) => {
                          const newPrompts = [...batchPrompts];
                          newPrompts[idx] = e.target.value;
                          setBatchPrompts(newPrompts);
                        }}
                        disabled={loading}
                      />
                    </div>
                  ))}
                </div>
                
                <button
                  className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50 font-medium text-sm"
                  onClick={() => setBatchPrompts([...batchPrompts, ''])}
                  disabled={loading}
                >
                  ➕ Add Operation
                </button>

                <button
                  className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50 font-medium"
                  onClick={handleBatchSubmit}
                  disabled={loading || batchPrompts.length === 0 || batchPrompts.every(p => !p.trim())}
                >
                  {loading ? '⏳ Processing...' : `✅ Apply All (${batchPrompts.filter(p => p.trim()).length})`}
                </button>
              </>
            )}

            {error && (
              <div className="p-3 bg-red-100 border border-red-300 rounded text-red-700 text-sm">
                ⚠️ {error}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
