import React, { useState } from 'react'
import api from '../services/api'

export default function Converter() {
  const [fileId, setFileId] = useState(null)
  const [latex, setLatex] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleUpload = async (e) => {
    setError(null)
    const f = e.target.files[0]
    if (!f) return
    setLoading(true)
    try {
      const res = await api.uploadFile(f)
      setFileId(res.file_id)
    } catch (err) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleConvert = async () => {
    if (!fileId) return setError('Upload a PDF first')
    setError(null)
    setLoading(true)
    try {
      const resp = await api.convertPdfToLatex({ 
        file_id: fileId,
        mathpix_app_id: null,  // Use default from environment
        mathpix_app_key: null  // Use default from environment
      })
      setLatex(resp.latex_content || '')
    } catch (err) {
      setError(err.message || 'Conversion failed')
    } finally {
      setLoading(false)
    }
  }

  const downloadTex = () => {
    const blob = new Blob([latex], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = (fileId || 'converted') + '.tex'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-700">PDF → LaTeX Converter</h1>

      <div className="bg-white shadow-sm border rounded p-4">
        <label className="block mb-2 text-sm font-medium">Upload PDF</label>
        <input type="file" accept=".pdf" onChange={handleUpload} />
        {loading && <div className="mt-2 text-sm text-blue-600">Processing...</div>}
        {error && <div className="mt-2 text-sm text-red-600">{error}</div>}

        <div className="mt-4">
          <button className="btn-primary" onClick={handleConvert} disabled={loading}>Convert to LaTeX</button>
          {latex && (
            <button className="ml-3 btn-outline" onClick={downloadTex}>Download .tex</button>
          )}
        </div>
      </div>

      {latex && (
        <div className="bg-white border p-4 rounded">
          <h2 className="font-medium mb-2">LaTeX Output</h2>
          <textarea className="w-full h-96 p-2 border rounded font-mono text-sm" value={latex} readOnly />
        </div>
      )}
    </div>
  )
}
