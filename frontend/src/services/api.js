import axios from 'axios'

// Base configuration
// Use environment variable if available, otherwise default to local development
const getBaseURL = () => {
  if (import.meta.env && import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE
  }
  // Default to localhost for development, can be overridden via env
  const isProduction = import.meta.env.PROD
  if (isProduction) {
    // In production, use the backend URL if available
    return process.env.VITE_API_BASE || 'http://localhost:8000'
  }
  // Development: use localhost
  return 'http://localhost:8000'
}

const BASE_URL = getBaseURL()

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 300000, // 5 minutes timeout for longer operations
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

// File Management
async function uploadFile(file) {
  const allowedTypes = ['application/pdf', 'application/x-tex', 'application/zip', 'application/x-latex']
  const fileExtension = file.name.split('.').pop().toLowerCase()
  const isValidType = allowedTypes.includes(file.type) || 
                     ['.pdf', '.tex', '.zip'].includes(`.${fileExtension}`)
  
  if (!isValidType) {
    throw new Error('Please upload a valid PDF, LaTeX (.tex), or ZIP file')
  }

  if (file.size > 50 * 1024 * 1024) { // 50MB limit
    throw new Error('File size exceeds the 50MB limit')
  }

  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await client.post('/api/v1/files/upload', formData, {
      headers: { 
        'Content-Type': 'multipart/form-data'
      },
      timeout: 180000 // 3 minutes for upload
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message ||
                        'Upload failed. Please try again.'
    throw new Error(errorMessage)
  }
}

function getFileUrl(fileId) {
  if (!fileId) return null
  return `${BASE_URL}/api/v1/files/download/${fileId}`
}

async function listFiles() {
  try {
    const response = await client.get('/api/v1/files/list')
    return response.data.files || []
  } catch (error) {
    console.error('Error listing files:', error)
    return []
  }
}

async function deleteFile(fileId) {
  try {
    const response = await client.delete(`/api/v1/files/delete/${fileId}`)
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.message ||
                        'Failed to delete file'
    throw new Error(errorMessage)
  }
}

// Document Editing
async function editDocument({ file_id, prompt, compile_pdf = false, images_dir_id = null }) {
  try {
    const response = await client.post('/api/v1/edit/edit-doc-v1', {
      file_id,
      prompt,
      compile_pdf,
      images_dir_id
    }, {
      timeout: 300000 // 5 minutes for document editing
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'Document editing failed. Please try again.'
    throw new Error(errorMessage)
  }
}

// LaTeX Compilation
async function compilePdf({ file_id, engine = 'pdflatex', images_dir_id = null }) {
  try {
    const response = await client.post('/api/v1/compile/pdf', {
      file_id,
      engine,
      images_dir_id
    }, {
      timeout: 300000 // 5 minutes for compilation
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'PDF compilation failed. Please check your LaTeX code.'
    throw new Error(errorMessage)
  }
}

// File Download
async function downloadFile(fileId, filename = 'document') {
  try {
    const response = await client.get(`/api/v1/files/download/${fileId}`, {
      responseType: 'blob',
      timeout: 180000 // 3 minutes for download
    })
    
    // Extract filename from content-disposition header if available
    const contentDisposition = response.headers['content-disposition'] || ''
    const match = contentDisposition.match(/filename="?([^"]+)"?/)
    const downloadFilename = match ? match[1] : `${filename}.pdf`
    
    // Create download link and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', downloadFilename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    
    return { success: true, filename: downloadFilename }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        'Download failed. The file may have been moved or deleted.'
    throw new Error(errorMessage)
  }
}

// LaTeX Fixing with RAG
async function fixLatexRag({
  file_id,
  document_type = 'research',
  conference = 'IEEE',
  column_format = '2-column',
  converted = true,
  original_format = 'PDF',
  compile_pdf = true
}) {
  try {
    const response = await client.post('/api/v1/fix/latex-rag', {
      file_id,
      document_type,
      conference,
      column_format,
      converted,
      original_format,
      compile_pdf
    }, {
      timeout: 300000 // 5 minutes for fixing
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        'Failed to fix LaTeX document. Please try again.'
    throw new Error(errorMessage)
  }
}

// PDF to LaTeX Conversion
async function convertPdfToLatex({ file_id, mathpix_app_id = null, mathpix_app_key = null }) {
  try {
    const response = await client.post('/api/v1/convert/pdf-to-latex', {
      file_id,
      mathpix_app_id,
      mathpix_app_key
    }, {
      timeout: 300000 // 5 minutes for conversion
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        'PDF to LaTeX conversion failed. Please ensure the PDF contains extractable text.'
    throw new Error(errorMessage)
  }
}

// Document Batch Editing
async function batchEditDocument({ file_id, queries, compile_pdf = false, delay = 1.5, images_dir_id = null }) {
  try {
    const response = await client.post('/api/v1/edit/batch-edit-v1', {
      file_id,
      queries,
      compile_pdf,
      delay,
      images_dir_id
    }, {
      timeout: 600000 // 10 minutes for batch operations
    })
    return response.data
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error ||
                        'Batch document editing failed. Please try again.'
    throw new Error(errorMessage)
  }
}

// Health Check
async function checkHealth() {
  try {
    const response = await client.get('/health', { timeout: 5000 })
    return response.data
  } catch (error) {
    return { status: 'unhealthy', error: error.message }
  }
}

export default {
  // File Management
  uploadFile,
  getFileUrl,
  listFiles,
  deleteFile,
  downloadFile,
  
  // Document Operations
  editDocument,
  batchEditDocument,
  compilePdf,
  fixLatexRag,
  convertPdfToLatex,
  
  // System
  checkHealth
}
