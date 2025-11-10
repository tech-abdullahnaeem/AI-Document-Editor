# FastAPI Document Editor - API Endpoints Documentation

## Overview
This document describes all active endpoints in the LaTeX Document Editing API. Each endpoint includes input/output specifications and usage examples.

---

## 1. Health Check

### `GET /health`
Check if the API server is running and healthy.

**Input:** None (Query Parameters)

**Output:**
```json
{
  "status": "healthy",
  "service": "LaTeX Document Editing API",
  "version": "1.0.0",
  "gemini_api_configured": true,
  "mathpix_api_configured": true
}
```

**Usage:**
```bash
curl http://localhost:8000/health
```

---

## 2. File Management

### `POST /api/v1/files/upload`
Upload a LaTeX document file to the server.

**Input:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): LaTeX file (.tex) to upload

**Output:**
```json
{
  "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
  "filename": "glucobench.tex",
  "file_size": 24640,
  "upload_time": "2025-11-10T17:56:10.910332",
  "message": "File uploaded successfully"
}
```

**Usage:**
```bash
curl -X POST -F "file=@glucobench.tex" http://localhost:8000/api/v1/files/upload
```

**Python Example:**
```python
import requests

files = {"file": ("glucobench.tex", open("glucobench.tex", "rb"))}
response = requests.post("http://localhost:8000/api/v1/files/upload", files=files)
file_id = response.json()["file_id"]
```

---

### `GET /api/v1/files/download/{file_id}`
Download a file (edited LaTeX or compiled PDF) by its ID.

**Input:**
- **Path Parameters:**
  - `file_id` (required): UUID of the file to download

**Output:**
- Binary file content (LaTeX .tex or PDF .pdf)
- **Headers:**
  - `Content-Type`: application/pdf or text/plain
  - `Content-Disposition`: attachment; filename="{filename}"

**Usage:**
```bash
curl -O http://localhost:8000/api/v1/files/download/a5aa8eee-1e70-4568-8215-feeb89603a8e
```

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/api/v1/files/download/a5aa8eee-1e70-4568-8215-feeb89603a8e")
with open("downloaded_file.pdf", "wb") as f:
    f.write(response.content)
```

---

## 3. LaTeX Compilation

### `POST /api/v1/compile/pdf`
Compile a LaTeX document to PDF using pdflatex, xelatex, or lualatex.

**Input:**
```json
{
  "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
  "engine": "pdflatex"
}
```

**Input Fields:**
- `file_id` (required): UUID of the LaTeX file to compile
- `engine` (optional, default: "pdflatex"): LaTeX engine to use
  - Options: `pdflatex`, `xelatex`, `lualatex`

**Output:**
```json
{
  "success": true,
  "pdf_id": "0b77d7c4-5d9f-4233-8909-91411f4df32c",
  "compilation_time": 1.62,
  "log": "SUCCESS: PDF generated successfully with pdflatex",
  "warnings": [],
  "errors": [],
  "message": "LaTeX compiled successfully (copied 0 images)"
}
```

**Output Fields:**
- `success` (boolean): Compilation success status
- `pdf_id` (string): UUID of the compiled PDF file
- `compilation_time` (float): Time taken in seconds
- `log` (string): Compilation log output
- `warnings` (array): List of LaTeX warnings
- `errors` (array): List of compilation errors
- `message` (string): Status message

**Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/compile/pdf \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "engine": "pdflatex"
  }'
```

**Python Example:**
```python
import requests

payload = {
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "engine": "pdflatex"
}

response = requests.post(
    "http://localhost:8000/api/v1/compile/pdf",
    json=payload,
    timeout=30
)

result = response.json()
if result['success']:
    print(f"PDF compiled: {result['pdf_id']}")
    print(f"Compilation time: {result['compilation_time']:.2f}s")
    
    # Download the PDF
    pdf_response = requests.get(
        f"http://localhost:8000/api/v1/files/download/{result['pdf_id']}"
    )
    with open("compiled.pdf", "wb") as f:
        f.write(pdf_response.content)
```

**Features:**
- ✅ Supports multiple LaTeX engines (pdflatex, xelatex, lualatex)
- ✅ Automatic image directory handling
- ✅ Two-pass compilation for references and citations
- ✅ Detailed compilation logs and error reporting
- ✅ Automatic cleanup of auxiliary files

---

## 4. Document Editing

### `POST /api/v1/edit/edit-doc-v1`
Edit a single LaTeX document with natural language instructions.

**Input:**
```json
{
  "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
  "prompt": "replace 'glucose' with 'blood glucose'",
  "compile_pdf": true,
  "images_dir_id": null
}
```

**Input Fields:**
- `file_id` (required): UUID of uploaded file
- `prompt` (required): Natural language instruction for editing
- `compile_pdf` (optional, default: false): Whether to compile result to PDF
- `images_dir_id` (optional): Directory ID containing images for compilation

**Supported Operations:**
- **Replace:** `"replace 'old text' with 'new text'"`
- **Format:** `"make 'text' bold"`, `"highlight 'text' in yellow"`
- **Remove:** `"remove all tables"`, `"delete the word 'deprecated'"`
- **Add:** `"add a conclusion section"`
- **Modify:** `"improve the introduction"`

**Output:**
```json
{
  "success": true,
  "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068_v1_edited.tex",
  "pdf_id": "a5aa8eee-1e70-4568-8215-feeb89603a8e",
  "operation": "replace",
  "action": "replace_word",
  "changes": 23,
  "processing_time": 4.32,
  "parsed_query": {
    "operation": "replace",
    "action": "replace_word",
    "target": "glucose",
    "replacement": "blood glucose",
    "target_type": "word",
    "confidence": 95
  },
  "message": "Successfully edited document"
}
```

**Output Fields:**
- `success` (boolean): Operation success status
- `file_id` (string): UUID of edited LaTeX file
- `pdf_id` (string, nullable): UUID of compiled PDF if compile_pdf=true
- `operation` (string): Type of operation (replace, format, remove, add, modify)
- `action` (string): Specific action performed
- `changes` (integer): Number of replacements/changes made
- `processing_time` (float): Time taken in seconds
- `parsed_query` (object): Breakdown of parsed user query
- `message` (string): Status message

**Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/edit/edit-doc-v1 \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "prompt": "replace glucose with blood glucose",
    "compile_pdf": true
  }'
```

**Python Example:**
```python
import requests

payload = {
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "prompt": "make the word Methods bold",
    "compile_pdf": True
}

response = requests.post(
    "http://localhost:8000/api/v1/edit/edit-doc-v1",
    json=payload,
    timeout=60
)

result = response.json()
print(f"Changes made: {result['changes']}")
print(f"PDF ID: {result['pdf_id']}")
```

---

### `POST /api/v1/edit/batch-edit-v1`
Apply multiple sequential edits to a LaTeX document in a single batch request.

**Input:**
```json
{
  "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
  "queries": [
    "replace 'glucose' with 'blood glucose'",
    "replace 'diabetes' with 'type 2 diabetes'",
    "make 'Conclusion' bold",
    "highlight 'Abstract' in yellow"
  ],
  "compile_pdf": true,
  "delay": 1.5
}
```

**Input Fields:**
- `file_id` (required): UUID of uploaded file
- `queries` (required): List of natural language editing instructions (minimum 1)
- `compile_pdf` (optional, default: false): Whether to compile final result to PDF
- `delay` (optional, default: 0): Delay between operations in seconds (for rate limiting)

**Output:**
```json
{
  "success": true,
  "file_id": "86dd414d-82ed-425f-bd47-dc1f44f0d121",
  "pdf_id": "5233cb80-2589-4aae-8444-765774eeabd1",
  "total_operations": 4,
  "successful_operations": 4,
  "failed_operations": 0,
  "results": [
    {
      "operation_id": 1,
      "success": true,
      "operation": "replace",
      "action": "replace_word",
      "changes": 23,
      "query": "replace 'glucose' with 'blood glucose'",
      "message": "Successfully replaced 23 occurrences"
    },
    {
      "operation_id": 2,
      "success": true,
      "operation": "replace",
      "action": "replace_word",
      "changes": 13,
      "query": "replace 'diabetes' with 'type 2 diabetes'",
      "message": "Successfully replaced 13 occurrences"
    },
    {
      "operation_id": 3,
      "success": true,
      "operation": "format",
      "action": "bold_word",
      "changes": 1,
      "query": "make 'Conclusion' bold",
      "message": "Successfully formatted 1 occurrence"
    },
    {
      "operation_id": 4,
      "success": true,
      "operation": "format",
      "action": "highlight_word",
      "changes": 2,
      "query": "highlight 'Abstract' in yellow",
      "message": "Successfully formatted 2 occurrences"
    }
  ],
  "processing_time": 29.51,
  "message": "Batch processing completed: 4/4 operations successful"
}
```

**Output Fields:**
- `success` (boolean): Overall batch operation success
- `file_id` (string): UUID of final edited file
- `pdf_id` (string, nullable): UUID of compiled PDF if compile_pdf=true
- `total_operations` (integer): Total queries submitted
- `successful_operations` (integer): Number of successful operations
- `failed_operations` (integer): Number of failed operations
- `results` (array): Detailed results for each operation
  - `operation_id`: Sequence number (1-indexed)
  - `success`: Operation success status
  - `operation`: Type of operation
  - `action`: Specific action performed
  - `changes`: Number of changes made
  - `query`: Original user query
  - `message`: Status message
- `processing_time` (float): Total time in seconds
- `message` (string): Summary message

**Processing Behavior:**
- Operations are applied **sequentially** - each operation modifies the result of the previous one
- If an operation fails (returns 0 changes), the error is recorded but processing continues
- Each operation uses the file state from the previous operation
- Total processing time = sum of individual times + delays between operations

**Usage:**
```bash
curl -X POST http://localhost:8000/api/v1/edit/batch-edit-v1 \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "queries": [
      "replace glucose with blood glucose",
      "make Methods bold"
    ],
    "compile_pdf": true,
    "delay": 1.0
  }'
```

**Python Example:**
```python
import requests

payload = {
    "file_id": "fc5b17be-11ef-409d-ae9f-ae3928dc1068",
    "queries": [
        "replace 'accuracy' with 'precision'",
        "replace 'algorithm' with 'method'",
        "make 'Results' bold",
        "highlight 'Important' in yellow"
    ],
    "compile_pdf": True,
    "delay": 1.5
}

response = requests.post(
    "http://localhost:8000/api/v1/edit/batch-edit-v1",
    json=payload,
    timeout=120
)

result = response.json()
print(f"Total operations: {result['total_operations']}")
print(f"Successful: {result['successful_operations']}")
print(f"Failed: {result['failed_operations']}")
print(f"Processing time: {result['processing_time']:.2f}s")

for op in result['results']:
    if op['success']:
        print(f"✅ Op {op['operation_id']}: {op['changes']} changes")
    else:
        print(f"❌ Op {op['operation_id']}: {op['message']}")
```

---

## 5. Supported Edit Operations

### Section Positioning (New Feature)
The V1 editor supports precise section positioning with `before`, `after`, and `end` placement:

**Syntax:**
- **Before existing section:** `"add section 'SectionName' before TargetSection"`
- **After existing section:** `"add section 'SectionName' after TargetSection"`
- **At document end:** `"add section 'SectionName' at the end"` or just `"add section 'SectionName'"`

**Examples:**
```python
# Add before unnumbered section
"add section 'Discussion' before Limitations"

# Add after numbered section
"add section 'Data Quality' after 3 Data"

# Add before first section
"add section 'Abstract' before 1 Introduction"

# Add at end (default)
"add section 'Appendix'"
```

**Features:**
- ✅ Works with numbered sections (e.g., "1 Introduction", "2 Methods")
- ✅ Works with unnumbered sections (e.g., "Limitations", "Acknowledgments")
- ✅ Auto-generates section content using AI
- ✅ Smart fallback: if target section not found, adds at end
- ✅ Target cleaning: automatically handles "section" word in queries

**Testing:**
- Comprehensive test suite available: `test_section_positioning.py`
- 100% success rate on all positioning tests
- Verified with 6 different positioning scenarios

---

## 6. Edit Operation Details

### Replace Operations
- **Word-level:** `"replace 'word' with 'replacement'"`
- **Phrase-level:** `"replace 'multi-word phrase' with 'new phrase'"`
- **Sentence-level:** `"replace 'sentence here.' with 'new sentence.'"`
- **Section-level:** `"replace 'section content' with 'new content'"`

### Format Operations
- **Bold:** `"make 'text' bold"`, `"bold 'text'"`
- **Italic:** `"make 'text' italic"`, `"italicize 'text'"`
- **Highlight:** `"highlight 'text' in yellow"`, `"highlight 'text'"` (default color)
- **Colors:** yellow, blue, red, green, orange, purple

### Remove Operations
- **Word:** `"remove the word 'deprecated'"`
- **Phrase:** `"remove 'multi-word phrase'"`
- **Sentence:** `"remove sentences containing 'text'"`
- **Section:** `"remove all tables"`, `"remove the appendix"`

### Add Operations
- **Sentence:** `"add a summary sentence after the introduction"`
- **Section:** `"add a new conclusion section"`
- **Section with positioning:** 
  - `"add section 'Discussion' before Limitations"`
  - `"add section 'Future Work' after Conclusion"`
  - `"add section 'Appendix' before 1 Introduction"`
  - `"add section 'Data Availability' at the end"`
- **Text:** `"add 'custom text' to the end of the document"`

### Modify Operations
- **AI-powered improvement:** `"improve the writing in the abstract"`
- **Enhancement:** `"make the introduction more engaging"`
- **Correction:** `"fix any grammatical errors in the methodology"`

---

## 7. Error Handling

### Error Response Format
```json
{
  "error": "File not found",
  "detail": "The specified file ID does not exist in the system"
}
```

### Common HTTP Status Codes
- **200 OK:** Request successful
- **201 Created:** File uploaded successfully
- **400 Bad Request:** Invalid input parameters
- **404 Not Found:** File not found
- **500 Internal Server Error:** Server error or compilation failure

### Common Error Messages
- `"File not found"` - File ID doesn't exist
- `"Editing failed: Unknown error during editing"` - Editor encountered an error
- `"queries must be a non-empty list"` - Batch endpoint requires at least one query
- `"Failed to parse query"` - Natural language parsing failed

---

## 8. Example Workflows

### Workflow 1: Simple Document Edit with PDF
```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Upload document
with open("document.tex", "rb") as f:
    files = {"file": ("document.tex", f)}
    response = requests.post(f"{BASE_URL}/api/v1/files/upload", files=files)
    file_id = response.json()["file_id"]

# Step 2: Edit and compile to PDF
payload = {
    "file_id": file_id,
    "prompt": "replace 'test' with 'evaluation'",
    "compile_pdf": True
}
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=60)
result = response.json()

# Step 3: Download PDF
pdf_response = requests.get(f"{BASE_URL}/api/v1/files/download/{result['pdf_id']}")
with open("output.pdf", "wb") as f:
    f.write(pdf_response.content)
```

### Workflow 2: Batch Processing with Multiple Edits
```python
import requests

BASE_URL = "http://localhost:8000"

# Step 1: Upload document
with open("research.tex", "rb") as f:
    files = {"file": ("research.tex", f)}
    response = requests.post(f"{BASE_URL}/api/v1/files/upload", files=files)
    file_id = response.json()["file_id"]

# Step 2: Apply batch edits
payload = {
    "file_id": file_id,
    "queries": [
        "replace 'AI' with 'Artificial Intelligence'",
        "replace 'ML' with 'Machine Learning'",
        "make 'Abstract' bold",
        "make 'Conclusion' bold",
        "highlight 'important findings' in yellow"
    ],
    "compile_pdf": True,
    "delay": 1.5
}

response = requests.post(
    f"{BASE_URL}/api/v1/edit/batch-edit-v1",
    json=payload,
    timeout=300
)
result = response.json()

print(f"Operations completed: {result['total_operations']}")
print(f"Successful: {result['successful_operations']}")
print(f"Failed: {result['failed_operations']}")

# Step 3: Download PDF
if result['pdf_id']:
    pdf_response = requests.get(f"{BASE_URL}/api/v1/files/download/{result['pdf_id']}")
    with open("research_edited.pdf", "wb") as f:
        f.write(pdf_response.content)
```

---

## 9. Performance Notes

- **Single edit processing:** 2-5 seconds
- **Batch operations:** ~2-3 seconds per operation + configured delay
- **PDF compilation:** 3-8 seconds (included in processing time)
- **Section positioning:** 15-25 seconds (includes AI content generation)
- **File size limit:** Up to 1 MB recommended
- **API timeout:** Set to 60+ seconds for batch operations with compilation

---

## 10. API Key Management & Rate Limiting

**Intelligent Rate Limit Handling:**
- **40 rotating Gemini API keys** for query parsing
- **Auto-reset mechanism:** Rate-limited keys automatically reset after 60 seconds
- **Success-based recovery:** Keys immediately restored when successful requests occur
- **Free tier limits:** 15 requests/minute per key
- **Total capacity:** ~600 requests/minute across all keys
- **Model:** gemini-2.0-flash-exp for query parsing

**Rate Limit Features:**
- ✅ Timestamp-based tracking with automatic expiration
- ✅ No permanent key blocking
- ✅ Self-healing system with cooldown periods
- ✅ Real-time cooldown timer in error messages
- ✅ Ignores false-positive ALTS gRPC warnings

---

## 11. Configuration & Environment

**Server:**
- Port: 8000
- Host: 0.0.0.0 (accessible from anywhere)
- API Base URL: `http://localhost:8000`
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative Documentation (ReDoc): `http://localhost:8000/redoc`

**Editor Implementation:**
- New Editor V1: Uses `/new editor /` folder
  - Advanced query parsing with Gemini 2.0 Flash
  - Modular architecture (document_editor, query_parser, add, modify, remove, replace, format)
  - Section positioning with before/after/end placement
  - AI-powered content generation
- RAG Fixer: Uses `/Rag latex fixer/` folder (independent implementation)
- Compiler: Uses `src/doc_edit/latex_compiler.py` for PDF compilation

---

## 12. Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check server status |
| `/api/v1/files/upload` | POST | Upload LaTeX document |
| `/api/v1/files/download/{file_id}` | GET | Download file (LaTeX or PDF) |
| `/api/v1/edit/edit-doc-v1` | POST | Single document edit (V1 - New Editor) |
| `/api/v1/edit/batch-edit-v1` | POST | Multiple sequential edits (V1 - New Editor) |
| `/api/v1/compile/pdf` | POST | Compile LaTeX to PDF |
| `/api/v1/fix/latex-rag` | POST | RAG-based LaTeX fixing |
| `/api/v1/convert/pdf-to-latex` | POST | Convert PDF to LaTeX via MathPix |

---

**Last Updated:** November 10, 2025  
**API Version:** 1.0.0  
**Status:** Production Ready  
**Recent Updates:**
- ✅ Section positioning with before/after/end placement (Nov 10, 2025)
- ✅ Intelligent rate limit handling with 60s auto-reset (Nov 10, 2025)
- ✅ Compiler endpoint fixed (removed incorrect await) (Nov 10, 2025)
- ✅ Query parser improvements for section name extraction (Nov 10, 2025)
