# AI Document Editor - Complete API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Codes](#error-codes)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)
8. [SDK Integration](#sdk-integration)

---

## Overview

The AI Document Editor API provides RESTful endpoints for document processing, including:
- Document upload and management
- Natural language document editing
- PDF to LaTeX conversion
- LaTeX compilation
- RAG-based document fixing

**Base URL:** `http://localhost:8000`

**API Version:** v1

**Content-Type:** `application/json`

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

**Future Enhancement:** API key-based authentication may be implemented.

---

## Endpoints

### File Management Endpoints

#### 1. Upload File
**POST** `/api/v1/files/upload`

Upload a LaTeX or PDF file for processing.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@document.pdf"
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | LaTeX (.tex, .latex) or PDF (.pdf) file |

**Response (200 OK):**
```json
{
  "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
  "filename": "document.pdf",
  "file_size": 512338,
  "upload_time": "2025-11-11T00:26:36.652167",
  "message": "File uploaded successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "No file provided"
}
```

**Response (413 Payload Too Large):**
```json
{
  "error": "File size exceeds maximum allowed size"
}
```

---

#### 2. Get File Info
**GET** `/api/v1/files/{file_id}`

Retrieve information about an uploaded file.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/files/378dad3c-bc7f-4bb9-abe5-d17bf88fda17"
```

**Response (200 OK):**
```json
{
  "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
  "filename": "document.pdf",
  "file_size": 512338,
  "file_type": "pdf",
  "upload_time": "2025-11-11T00:26:36",
  "last_modified": "2025-11-11T00:35:22",
  "status": "processed"
}
```

**Response (404 Not Found):**
```json
{
  "error": "File not found"
}
```

---

#### 3. Delete File
**DELETE** `/api/v1/files/{file_id}`

Delete an uploaded file and all associated data.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/files/378dad3c-bc7f-4bb9-abe5-d17bf88fda17"
```

**Response (200 OK):**
```json
{
  "message": "File deleted successfully",
  "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17"
}
```

**Response (404 Not Found):**
```json
{
  "error": "File not found"
}
```

---

### Document Editing Endpoints

#### 1. Edit Document with Natural Language
**POST** `/api/v1/edit/edit-doc-v1`

Apply natural language instructions to edit a document.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "prompt": "remove all tables"
  }'
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_id | string | Yes | File ID from upload endpoint |
| prompt | string | Yes | Natural language instruction |

**Valid Operations:**
- `remove` - Delete content (words, phrases, sections, tables, equations)
- `replace` - Substitute content with new text
- `add` - Insert new content
- `format` - Apply formatting (highlight, bold, italic)
- `modify` - General modifications

**Response (200 OK):**
```json
{
  "success": true,
  "file_id": "935f7544-f59b-4a90-b9a5-bf14de1fa443",
  "pdf_id": null,
  "operation": "remove",
  "action": "remove_table",
  "changes": 6,
  "processing_time": 3.739884614944458,
  "parsed_query": {
    "operation": "remove",
    "action": "remove_table",
    "target": "all",
    "new_text": null,
    "target_type": "table",
    "format_action": null,
    "color": null,
    "section_name": null,
    "position": null,
    "convert_to_latex": false,
    "confidence": 0.95
  },
  "message": "Document edited successfully. Operation: remove/remove_table, Changes: 6"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid file_id",
  "details": "File not found"
}
```

**Response (422 Unprocessable Entity):**
```json
{
  "error": "Failed to parse prompt",
  "details": "AI parsing returned unexpected format"
}
```

---

### LaTeX Fixing Endpoints

#### 1. Fix LaTeX with RAG
**POST** `/api/v1/fix/latex-rag`

Apply RAG-based contextual fixes to LaTeX documents. Optionally converts PDFs to LaTeX using Mathpix.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/fix/latex-rag" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "2e727a83-b622-4979-8b4b-1ea2998d0b4b",
    "document_type": "research",
    "conference": "IEEE",
    "column_format": "2-column",
    "converted": true,
    "original_format": "PDF",
    "compile_pdf": false
  }'
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| file_id | string | Yes | - | File ID to fix |
| document_type | string | No | "research" | Document type: "research" or "normal" |
| conference | string | No | "IEEE" | Conference type: "IEEE", "ACM", "NIPS", etc. |
| column_format | string | No | "2-column" | Column format: "1-column", "2-column" |
| converted | boolean | No | false | Whether document was converted from PDF |
| original_format | string | No | null | Original format: "PDF", "Word", "RTF" |
| compile_pdf | boolean | No | true | Whether to compile to PDF after fixing |
| images_dir_id | string | No | null | Optional images directory file ID |

**Document Types:**
- `research` - Research paper format
- `normal` - Standard document format

**Conference Types:**
- `IEEE` - IEEE conference format
- `ACM` - ACM conference format
- `NIPS` - Neural Information Processing Systems
- `ICML` - International Conference on Machine Learning
- `NeurIPS` - Conference on Neural Information Processing Systems
- `ECCV` - European Conference on Computer Vision
- `ICCV` - International Conference on Computer Vision

**Column Formats:**
- `1-column`
- `2-column`

**Response (200 OK):**
```json
{
  "success": true,
  "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
  "pdf_id": null,
  "issues_found": 62,
  "issues_fixed": 62,
  "processing_time": 55.65655493736267,
  "images_copied": 24,
  "output_directory": "/path/to/output",
  "converted_from_pdf": true,
  "mathpix_metadata": {
    "conversion_method": "official_sdk_mpxpy",
    "main_file": "2025_11_10_be1e3f6dfe7da4cda3ecg.tex",
    "total_tex_files": 1,
    "total_images": 6,
    "zip_size": 411404,
    "images_extracted": 6,
    "total_files_extracted": 7,
    "images_directory": "/path/to/images"
  },
  "report": {
    "total_issues": 62,
    "fixes_applied": 62,
    "table_fixes_applied": true,
    "document_type": "research",
    "conference": "IEEE",
    "column_format": "2-column",
    "rag_mode": "full_subprocess",
    "processing_steps": [
      "1. Table fixes",
      "2. RAG-based comprehensive fixes",
      "3. Image positioning",
      "4. Image size limiting",
      "5. Float parameters optimization",
      "6. PDF compilation"
    ],
    "subprocess_output": "..."
  },
  "message": "LaTeX document processed successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid document type",
  "details": "Supported types: research, normal"
}
```

**Response (404 Not Found):**
```json
{
  "error": "File not found",
  "file_id": "invalid_id"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "PDF conversion failed",
  "details": "Mathpix API error"
}
```

---

### PDF Compilation Endpoints

#### 1. Compile LaTeX to PDF
**POST** `/api/v1/compile/pdf`

Compile a LaTeX document to PDF using pdflatex or xelatex.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/compile/pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "engine": "pdflatex"
  }'
```

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| file_id | string | Yes | - | LaTeX file ID to compile |
| engine | string | No | "pdflatex" | Compilation engine: "pdflatex" or "xelatex" |

**Supported Engines:**
- `pdflatex` - Standard LaTeX to PDF compiler
- `xelatex` - Extended LaTeX with Unicode support

**Response (200 OK):**
```json
{
  "success": true,
  "pdf_id": "06813b26-5455-4e73-bb7d-b2144d9f68c2",
  "compilation_time": 1.57,
  "log": "LaTeX compilation log output...",
  "warnings": [],
  "errors": [],
  "message": "LaTeX compiled successfully (copied 21 images)"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid compilation engine",
  "details": "Supported engines: pdflatex, xelatex"
}
```

**Response (404 Not Found):**
```json
{
  "error": "File not found",
  "file_id": "invalid_id"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "LaTeX compilation failed",
  "details": "See log for details",
  "log": "... LaTeX error output ..."
}
```

---

## Request/Response Formats

### Standard Response Format

All successful responses follow this structure:

```json
{
  "success": true,
  "message": "Human-readable success message",
  "data": {
    "key": "value"
  }
}
```

### Error Response Format

All error responses follow this structure:

```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error description",
  "timestamp": "2025-11-11T00:26:36.652167"
}
```

### Request Headers

**Required Headers:**
```
Content-Type: application/json
```

**Optional Headers:**
```
Accept: application/json
User-Agent: YourApp/1.0
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | File or resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 422 | Unprocessable Entity | Request data validation failed |
| 500 | Internal Server Error | Server-side processing error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Types

| Error | Status | Description | Solution |
|-------|--------|-------------|----------|
| `File not found` | 404 | File ID doesn't exist | Verify file_id from upload response |
| `Invalid file_id` | 400 | File ID format invalid | Use UUID format from upload |
| `Failed to parse prompt` | 422 | Prompt unclear to AI parser | Rewrite prompt more clearly |
| `LaTeX compilation failed` | 500 | LaTeX syntax error | Check document for syntax errors |
| `Mathpix conversion failed` | 500 | PDF conversion error | Ensure PDF is valid |
| `No file provided` | 400 | Upload missing file | Include file in multipart/form-data |

---

## Rate Limiting

### Current Limits

- **Requests per minute:** Unlimited (no throttling)
- **File size limit:** 1GB per file
- **File count:** Unlimited
- **Concurrent uploads:** 10 simultaneous

### Future Rate Limiting

Rate limiting may be implemented with:
- 100 requests per minute per IP
- 1000 requests per hour per API key
- 50 concurrent operations per user

---

## Examples

### Example 1: Complete PDF Processing Workflow

```bash
#!/bin/bash

# Step 1: Upload PDF
UPLOAD=$(curl -s -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@research_paper.pdf")

FILE_ID=$(echo $UPLOAD | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
echo "Uploaded file: $FILE_ID"

# Step 2: Apply RAG fixer
FIX=$(curl -s -X POST "http://localhost:8000/api/v1/fix/latex-rag" \
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

FIXED_ID=$(echo $FIX | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
echo "Fixed file: $FIXED_ID"

# Step 3: Edit document
EDIT=$(curl -s -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$FIXED_ID\",
    \"prompt\": \"remove all tables and equations\"
  }")

EDITED_ID=$(echo $EDIT | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
echo "Edited file: $EDITED_ID"

# Step 4: Compile to PDF
COMPILE=$(curl -s -X POST "http://localhost:8000/api/v1/compile/pdf" \
  -H "Content-Type: application/json" \
  -d "{
    \"file_id\": \"$EDITED_ID\",
    \"engine\": \"pdflatex\"
  }")

PDF_ID=$(echo $COMPILE | python3 -c "import sys, json; print(json.load(sys.stdin)['pdf_id'])")
echo "Final PDF: $PDF_ID"
```

---

### Example 2: Document Editing Operations

```bash
# Remove a word
curl -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "prompt": "remove the word dataset"
  }'

# Replace terminology
curl -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "prompt": "replace AI with Artificial Intelligence"
  }'

# Add section
curl -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "prompt": "add a Future Work section before Conclusion"
  }'

# Highlight text
curl -X POST "http://localhost:8000/api/v1/edit/edit-doc-v1" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "378dad3c-bc7f-4bb9-abe5-d17bf88fda17",
    "prompt": "highlight the Introduction section with yellow"
  }'
```

---

## SDK Integration

### Python SDK Example

```python
import requests
import json

class AIDocumentEditorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def upload_file(self, file_path):
        """Upload a file and return file_id"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/api/v1/files/upload",
                files=files
            )
        return response.json()['file_id']
    
    def edit_document(self, file_id, prompt):
        """Edit document with natural language prompt"""
        response = self.session.post(
            f"{self.base_url}/api/v1/edit/edit-doc-v1",
            json={"file_id": file_id, "prompt": prompt}
        )
        return response.json()
    
    def fix_latex(self, file_id, document_type="research", conference="IEEE"):
        """Apply RAG fixer to document"""
        response = self.session.post(
            f"{self.base_url}/api/v1/fix/latex-rag",
            json={
                "file_id": file_id,
                "document_type": document_type,
                "conference": conference,
                "column_format": "2-column",
                "converted": True,
                "original_format": "PDF",
                "compile_pdf": False
            }
        )
        return response.json()
    
    def compile_pdf(self, file_id, engine="pdflatex"):
        """Compile LaTeX to PDF"""
        response = self.session.post(
            f"{self.base_url}/api/v1/compile/pdf",
            json={"file_id": file_id, "engine": engine}
        )
        return response.json()

# Usage Example
if __name__ == "__main__":
    client = AIDocumentEditorClient()
    
    # Upload
    file_id = client.upload_file("document.pdf")
    print(f"Uploaded: {file_id}")
    
    # Fix
    fix_result = client.fix_latex(file_id)
    print(f"Fixed: {fix_result['file_id']}")
    
    # Edit
    edit_result = client.edit_document(fix_result['file_id'], "remove all tables")
    print(f"Edited: {edit_result['file_id']}")
    
    # Compile
    compile_result = client.compile_pdf(edit_result['file_id'])
    print(f"PDF: {compile_result['pdf_id']}")
```

---

### JavaScript SDK Example

```javascript
class AIDocumentEditorClient {
    constructor(baseUrl = "http://localhost:8000") {
        this.baseUrl = baseUrl;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/api/v1/files/upload`, {
            method: 'POST',
            body: formData
        });
        
        return (await response.json()).file_id;
    }

    async editDocument(fileId, prompt) {
        const response = await fetch(`${this.baseUrl}/api/v1/edit/edit-doc-v1`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, prompt })
        });
        
        return await response.json();
    }

    async fixLatex(fileId, options = {}) {
        const defaults = {
            document_type: "research",
            conference: "IEEE",
            column_format: "2-column",
            converted: true,
            original_format: "PDF",
            compile_pdf: false
        };

        const response = await fetch(`${this.baseUrl}/api/v1/fix/latex-rag`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, ...defaults, ...options })
        });
        
        return await response.json();
    }

    async compilePdf(fileId, engine = "pdflatex") {
        const response = await fetch(`${this.baseUrl}/api/v1/compile/pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId, engine })
        });
        
        return await response.json();
    }
}

// Usage Example
(async () => {
    const client = new AIDocumentEditorClient();
    
    // Upload
    const fileInput = document.querySelector('input[type="file"]');
    const fileId = await client.uploadFile(fileInput.files[0]);
    console.log(`Uploaded: ${fileId}`);
    
    // Fix
    const fixResult = await client.fixLatex(fileId);
    console.log(`Fixed: ${fixResult.file_id}`);
    
    // Edit
    const editResult = await client.editDocument(fixResult.file_id, "remove all tables");
    console.log(`Edited: ${editResult.file_id}`);
    
    // Compile
    const compileResult = await client.compilePdf(editResult.file_id);
    console.log(`PDF: ${compileResult.pdf_id}`);
})();
```

---

## Support & Resources

### Documentation
- **Prompt Guide:** `PROMPT_GUIDE.md`
- **API Examples:** See examples section above
- **Configuration:** `config/` directory

### Troubleshooting
- Check server logs for detailed error messages
- Verify file_id from upload response
- Test endpoints with provided curl examples
- Review response status codes and error messages

### Contact & Support
- Submit issues to the project repository
- Check API logs at `/logs/api.log`
- Review server output for real-time processing details

---

## API Versioning

**Current Version:** v1

**Planned Updates:**
- v1.1 - API key authentication
- v1.2 - Rate limiting
- v1.3 - Additional document formats (Word, HTML)
- v2.0 - WebSocket support for real-time processing

---

## Changelog

### Version 1.0 (Current)
- ✅ Document upload and management
- ✅ Natural language document editing
- ✅ PDF to LaTeX conversion
- ✅ LaTeX compilation
- ✅ RAG-based document fixing

---

## Best Practices

1. **Always verify uploads** - Check the file_id returned from upload
2. **Chain operations** - Process files through multiple steps for best results
3. **Error handling** - Implement proper error handling for production use
4. **Timeout handling** - RAG fixing can take 40-60 seconds
5. **File cleanup** - Delete files after processing to save storage
6. **Logging** - Log all API calls for debugging

---

## Performance Tips

- Use `compile_pdf: false` when only fixing documents
- Batch similar edits in one prompt when possible
- Upload files directly instead of converting first
- Use `xelatex` for documents with Unicode characters
- Monitor server load for large batch operations

---

## Security Considerations

- Files are stored with unique UUIDs
- No authentication currently required (add for production)
- Validate input file types before processing
- Implement file size limits
- Add rate limiting for production
- Use HTTPS for sensitive documents
- Implement access control for multi-user environments
