# Document Editor API - Complete Documentation

## Base URL
```
Production: http://161.35.235.101:8001
Local: http://localhost:8000
```

## Interactive Documentation
- **Swagger UI**: `http://161.35.235.101:8001/docs`
- **ReDoc**: `http://161.35.235.101:8001/redoc`

---

## Table of Contents
1. [Health & Status](#health--status)
2. [File Management](#file-management)
3. [PDF to LaTeX Conversion](#pdf-to-latex-conversion)
4. [LaTeX Fixing (RAG)](#latex-fixing-rag)
5. [Document Editing (AI)](#document-editing-ai)
6. [LaTeX Compilation](#latex-compilation)
7. [Authentication](#authentication)

---

## Health & Status

### GET `/health`
Check API health and configuration status.

**Request:**
```bash
curl http://161.35.235.101:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "LaTeX Document Editing API",
  "version": "1.0.0",
  "gemini_api_configured": true,
  "mathpix_api_configured": true
}
```

### GET `/`
Get basic API information.

**Request:**
```bash
curl http://161.35.235.101:8001/
```

**Response:**
```json
{
  "message": "LaTeX Document Editing API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## File Management

### POST `/api/v1/files/upload`
Upload a file (PDF or LaTeX) to the server.

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/files/upload" \
  -F "file=@/path/to/document.pdf"
```

**Input:**
- **file** (required): File upload (PDF, .tex, .zip)
- Supported formats: `.pdf`, `.tex`, `.zip`
- Max size: 50MB

**Response:**
```json
{
  "file_id": "d40dd74e-2afe-4117-9b43-56eb2a507adb",
  "filename": "document.pdf",
  "file_size": 1146001,
  "upload_time": "2025-10-19T14:39:57.076375",
  "message": "File uploaded successfully"
}
```

**Status Codes:**
- `200`: File uploaded successfully
- `400`: Invalid file type or size
- `500`: Server error

---

### GET `/api/v1/files/download/{file_id}`
Download a file by its ID.

**Request:**
```bash
curl -X GET "http://161.35.235.101:8001/api/v1/files/download/{file_id}" \
  -o output_file.pdf
```

**Response:**
- Binary file content (PDF, TEX, ZIP)

**Status Codes:**
- `200`: File downloaded successfully
- `404`: File not found
- `500`: Server error

---

### GET `/api/v1/files/list`
List all uploaded files.

**Request:**
```bash
curl http://161.35.235.101:8001/api/v1/files/list
```

**Response:**
```json
{
  "files": [
    {
      "file_id": "d40dd74e-2afe-4117-9b43-56eb2a507adb",
      "filename": "document.pdf",
      "file_size": 1146001,
      "upload_time": "2025-10-19T14:39:57"
    }
  ],
  "total": 1
}
```

---

### DELETE `/api/v1/files/delete/{file_id}`
Delete a file by its ID.

**Request:**
```bash
curl -X DELETE "http://161.35.235.101:8001/api/v1/files/delete/{file_id}"
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_id": "d40dd74e-2afe-4117-9b43-56eb2a507adb"
}
```

---
<!-- #Not using this  -->
<!-- ## PDF to LaTeX Conversion

### POST `/api/v1/convert/pdf-to-latex`
Convert PDF to LaTeX using MathPix OCR.

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/convert/pdf-to-latex" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "file_id": "d40dd74e-2afe-4117-9b43-56eb2a507adb",
    "mathpix_app_id": "optional-custom-id",
    "mathpix_app_key": "optional-custom-key"
  }'
```

**Input:**
```json
{
  "file_id": "string (required)",
  "mathpix_app_id": "string (optional)",
  "mathpix_app_key": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "abc123-latex-file-id",
  "latex_content": "\\documentclass{article}...",
  "conversion_time": 12.5,
  "message": "PDF converted to LaTeX successfully",
  "warnings": ["Some equations may need manual review"]
}
```

**Status Codes:**
- `200`: Conversion successful
- `404`: File not found
- `500`: Conversion error

--- -->

## LaTeX Fixing (RAG)

### POST `/api/v1/fix/latex-rag`
Fix LaTeX document using RAG-based AI system.

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/fix/latex-rag" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "d40dd74e-2afe-4117-9b43-56eb2a507adb",
    "document_type": "research",    (document types = research or normal (options))
    "conference": "IEEE",   (conferences= ACM,IEEE, Generic)
    "column_format": "2-column", (column formats= 2-column , 1 column)
    "converted": true,
    "original_format": "PDF",
    "compile_pdf": false,
    "images_dir_id": null
  }'
```

**Input:**
```json
{
  "file_id": "string (required) - ID of uploaded PDF/LaTeX file",
  "document_type": "enum (research|normal) - default: research",
  "conference": "enum (IEEE|ACM|SPRINGER|ELSEVIER|GENERIC) - default: IEEE",
  "column_format": "enum (1-column|2-column) - default: 2-column",
  "converted": "boolean - Was document converted from PDF? default: false",
  "original_format": "enum (PDF|LATEX) - Original format",
  "compile_pdf": "boolean - Compile to PDF after fixing? default: true",
  "images_dir_id": "string (optional) - ID of images directory"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "a393293a-4783-483f-9b34-339d38444e34",
  "pdf_id": "optional-pdf-id-if-compiled",
  "issues_found": 62,
  "issues_fixed": 62,
  "processing_time": 36.78,
  "images_copied": 12,
  "output_directory": "/path/to/output",
  "converted_from_pdf": true,
  "mathpix_metadata": {
    "conversion_method": "official_sdk_mpxpy",
    "total_images": 6,
    "images_extracted": 6
  },
  "conversion_warnings": [],
  "report": {
    "total_issues": 62,
    "fixes_applied": 62,
    "success_rate": "100.0%",
    "processing_steps": [
      "1. Table fixes (a.py)",
      "2. RAG-based comprehensive fixes (subprocess)",
      "3. Image positioning ([!htbp])",
      "4. Image size limiting (50% width)"
    ]
  },
  "message": "✅ MathPix conversion SUCCESS | LaTeX document processed successfully"
}
```

**Processing Features:**
- ✅ PDF to LaTeX conversion (MathPix)
- ✅ Table structure fixing
- ✅ RAG-based contextual error detection
- ✅ Image extraction and positioning
- ✅ Conference-specific formatting
- ✅ Column format adjustment
- ✅ Citation and reference fixing
- ✅ Equation and math mode corrections

**Status Codes:**
- `200`: Processing successful
- `404`: File not found
- `500`: Processing error

---

## Document Editing (AI)

### POST `/api/v1/edit/prompt`
Edit document using natural language instructions (Gemini AI).

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/edit/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "a393293a-4783-483f-9b34-339d38444e34",
    "prompt": "change title to Stutter Detection in Urdu Language",
    "compile_pdf": false,
    "images_dir_id": null
  }'
```

**Input:**
```json
{
  "file_id": "string (required) - ID of LaTeX file",
  "prompt": "string (required) - Natural language editing instruction",
  "compile_pdf": "boolean - Compile to PDF after editing? default: true",
  "images_dir_id": "string (optional) - ID of images directory"
}
```

**Example Prompts:**
- `"change title to Stutter Detection in Urdu Language"`
- `"add a new section about machine learning after the introduction"`
- `"remove the limitations section"`
- `"highlight all text in the related work section in red"`
- `"change the abstract to be more concise"`
- `"fix all citations in IEEE format"`

**Response:**
```json
{
  "success": true,
  "file_id": "6371c6f1-1655-4153-a77c-ae65d55dd88c",
  "pdf_id": "optional-pdf-id-if-compiled",
  "edits_applied": 2,
  "processing_time": 16.99,
  "changes_summary": "Applied 2 surgical edits to document",
  "message": "Document edited successfully using CLI logic"
}
```

**AI Capabilities:**
- ✅ Title modification
- ✅ Section addition/removal
- ✅ Content highlighting
- ✅ Abstract rewriting
- ✅ Citation formatting
- ✅ Structural changes
- ✅ Text replacement
- ✅ Intelligent context understanding

**Status Codes:**
- `200`: Editing successful
- `404`: File not found
- `500`: Editing error

---
<!-- Not using -->
<!-- ### POST `/api/v1/edit/direct`
Edit LaTeX document by providing complete LaTeX code.

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/edit/direct" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "a393293a-4783-483f-9b34-339d38444e34",
    "latex_content": "\\documentclass{IEEEtran}\\begin{document}...\\end{document}",
    "compile_pdf": true
  }'
```

**Input:**
```json
{
  "file_id": "string (required) - Original file ID",
  "latex_content": "string (required) - Complete modified LaTeX code",
  "compile_pdf": "boolean - Compile to PDF? default: true"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "new-file-id",
  "pdf_id": "optional-pdf-id-if-compiled",
  "processing_time": 2.5,
  "message": "Direct edit applied successfully"
}
```

--- -->

## LaTeX Compilation

### POST `/api/v1/compile/pdf`
Compile LaTeX document to PDF.

**Request:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/compile/pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "6371c6f1-1655-4153-a77c-ae65d55dd88c",
    "engine": "pdflatex",
    "images_dir_id": null
  }'
```

**Input:**
```json
{
  "file_id": "string (required) - ID of LaTeX file",
  "engine": "string - LaTeX engine (pdflatex|xelatex|lualatex) default: pdflatex",
  "images_dir_id": "string (optional) - ID of images directory"
}
```

**LaTeX Engines:**
- **pdflatex**: Best for standard documents (fastest)
- **xelatex**: Best for Unicode and custom fonts
- **lualatex**: Best for complex documents and Lua scripting

**Response:**
```json
{
  "success": true,
  "pdf_id": "22faf90f-e55c-410c-be48-69d1450ecf89",
  "compilation_time": 1.55,
  "log": "LaTeX compilation log...",
  "warnings": [],
  "errors": [],
  "message": "LaTeX compiled successfully (copied 6 images)"
}
```

**Compilation Features:**
- ✅ Automatic image discovery and copying
- ✅ Multiple LaTeX engine support
- ✅ Error detection and reporting
- ✅ Warning collection
- ✅ Multi-pass compilation (for references)
- ✅ Detailed compilation logs

**Common Errors:**
- Missing packages → Install required LaTeX packages
- Image not found → Ensure images are uploaded
- Syntax errors → Review LaTeX code

**Status Codes:**
- `200`: Compilation successful
- `404`: File not found
- `500`: Compilation error

---

## Authentication

Most endpoints require API key authentication.

**Header:**
```
X-API-Key: your-secret-api-key
```

<!-- **Example:**
```bash
curl -X POST "http://161.35.235.101:8001/api/v1/convert/pdf-to-latex" \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "abc123"}'
``` -->

**Public Endpoints (No Auth Required):**
- `GET /health`
- `GET /`
- `GET /docs`
- `GET /redoc`

**Protected Endpoints (Auth Required):**
- `POST /api/v1/convert/*`
- `GET /api/v1/debug/*`

**Temporarily Disabled (For Testing):**
- Most other endpoints have auth temporarily disabled

---

## Complete Workflow Example

### Full Document Processing Pipeline

```bash
#!/bin/bash

API_URL="http://161.35.235.101:8001"

# Step 1: Upload PDF
echo "📤 Uploading PDF..."
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/files/upload" \
  -F "file=@document.pdf")
FILE_ID=$(echo $UPLOAD_RESPONSE | jq -r '.file_id')
echo "✅ File ID: $FILE_ID"

# Step 2: Fix LaTeX with RAG (includes PDF to LaTeX conversion)
echo "🔧 Processing with RAG fixer..."
FIX_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/fix/latex-rag" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FILE_ID\",
    \"document_type\": \"research\",
    \"conference\": \"IEEE\",
    \"column_format\": \"2-column\",
    \"converted\": true,
    \"original_format\": \"PDF\",
    \"compile_pdf\": false
  }")
FIXED_FILE_ID=$(echo $FIX_RESPONSE | jq -r '.file_id')
echo "✅ Fixed File ID: $FIXED_FILE_ID"

# Step 3: Edit with AI prompt
echo "✏️  Editing with AI..."
EDIT_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/edit/prompt" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FIXED_FILE_ID\",
    \"prompt\": \"change title to My New Title\",
    \"compile_pdf\": false
  }")
EDITED_FILE_ID=$(echo $EDIT_RESPONSE | jq -r '.file_id')
echo "✅ Edited File ID: $EDITED_FILE_ID"

# Step 4: Compile to PDF
echo "📄 Compiling to PDF..."
COMPILE_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/compile/pdf" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$EDITED_FILE_ID\",
    \"engine\": \"pdflatex\"
  }")
PDF_ID=$(echo $COMPILE_RESPONSE | jq -r '.pdf_id')
echo "✅ PDF ID: $PDF_ID"

# Step 5: Download final PDF
echo "⬇️  Downloading PDF..."
curl -X GET "$API_URL/api/v1/files/download/$PDF_ID" \
  -o final_document.pdf
echo "✅ Downloaded: final_document.pdf"
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "status_code": 500
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `403`: Forbidden (invalid API key)
- `404`: Not found (file or endpoint)
- `500`: Internal server error

---

## Rate Limits

- **Gemini AI**: 1,350 requests/day (27 API keys with auto-rotation)
- **MathPix**: Based on your subscription plan
- **File uploads**: 50MB per file
- **Concurrent requests**: Unlimited (async processing)

---

## Support & Issues

- **Documentation**: `/docs` (Swagger UI)
- **Health Check**: `/health`
- **GitHub**: https://github.com/abd84/AI-Document-Editor----v2-
- **Email**: support@example.com

---

## Version History

**v1.0.0** (Current)
- ✅ Full PDF to LaTeX conversion (MathPix)
- ✅ RAG-based LaTeX fixing
- ✅ AI-powered document editing (Gemini)
- ✅ LaTeX compilation with multiple engines
- ✅ Image handling and positioning
- ✅ Conference-specific formatting
- ✅ Comprehensive API key rotation

---

## Notes

- All file IDs are UUIDs (e.g., `d40dd74e-2afe-4117-9b43-56eb2a507adb`)
- Files are stored temporarily and may be cleaned up after 24 hours
- Image files should be in JPEG or PNG format
- LaTeX files should be valid UTF-8 encoded text
- Maximum processing time: 5 minutes per request

**Production Ready**: All endpoints tested and working on DigitalOcean server.
