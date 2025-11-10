# AI Document Editor - Complete Functionality & Prompt Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Operations](#core-operations)
3. [Supported Actions](#supported-actions)
4. [Prompt Writing Guide](#prompt-writing-guide)
5. [Examples](#examples)
6. [API Endpoints](#api-endpoints)
7. [File Management](#file-management)

---

## Overview

The AI Document Editor is a powerful FastAPI-based document processing system that allows natural language editing of LaTeX documents. It uses AI-powered query parsing to understand your intentions and apply the requested modifications.

**Key Features:**
- ✅ Natural language document editing
- ✅ PDF to LaTeX conversion (via Mathpix)
- ✅ RAG-based LaTeX fixing with contextual improvements
- ✅ Multiple document operations (add, remove, replace, format)
- ✅ PDF compilation to generate output
- ✅ Math content validation
- ✅ Multi-language support

---

## Core Operations

### 1. **REMOVE Operation**
Deletes content from documents with precision.

**Supported Target Types:**
- `word` - Remove individual words
- `phrase` - Remove phrases or sentences
- `sentence` - Remove complete sentences
- `section` - Remove entire sections
- `table` - Remove tables (supports table, tabular, longtable)
- `equation` - Remove mathematical equations with content validation

**Keywords that trigger removal:**
- "remove", "delete", "strip", "eliminate", "erase"

---

### 2. **REPLACE Operation**
Substitutes content with new text.

**Supported Target Types:**
- `word` - Replace words
- `phrase` - Replace phrases
- `sentence` - Replace sentences
- `section` - Replace entire sections

**Keywords that trigger replacement:**
- "replace", "substitute", "change", "swap", "update", "modify"

---

### 3. **ADD Operation**
Inserts new content into documents.

**Supported Target Types:**
- `word` - Add words
- `sentence` - Add sentences
- `section` - Add new sections
- `content` - Add general content

**Keywords that trigger addition:**
- "add", "insert", "include", "append", "create"

**Position Options:**
- `before` - Insert before target
- `after` - Insert after target
- `beginning` - Insert at document start
- `end` - Insert at document end

---

### 4. **FORMAT Operation**
Applies formatting to content without modifying text.

**Supported Actions:**
- `highlight_word` - Highlight specific words
- `highlight_section` - Highlight entire sections
- `bold_text` - Make text bold
- `italic_text` - Make text italic
- `underline_text` - Underline text

**Color Options (for highlighting):**
- yellow, red, blue, green, orange, purple, cyan, magenta, lime, pink, brown, gray

**Keywords that trigger formatting:**
- "highlight", "bold", "italic", "underline", "format", "emphasize"

---

## Supported Actions

| Operation | Action | Example |
|-----------|--------|---------|
| REMOVE | remove_word | Remove the word "dataset" |
| REMOVE | remove_phrase | Delete "machine learning models" |
| REMOVE | remove_sentence | Remove this sentence: "X" |
| REMOVE | remove_section | Remove the Methods section |
| REMOVE | remove_table | Remove all tables |
| REMOVE | remove_equation | Delete all equations |
| REPLACE | replace_word | Replace "AI" with "Artificial Intelligence" |
| REPLACE | replace_phrase | Change "deep learning" to "neural networks" |
| REPLACE | replace_section | Replace Introduction with new text |
| ADD | add_word | Add "innovative" before "approach" |
| ADD | add_sentence | Insert new conclusion sentence |
| ADD | add_section | Create Future Work section before Conclusion |
| FORMAT | highlight_word | Highlight "FluentNet" in yellow |
| FORMAT | highlight_section | Highlight Introduction with blue |
| FORMAT | bold_text | Make "important" bold |

---

## Prompt Writing Guide

### ✅ Best Practices for Writing Prompts

#### 1. **Be Clear and Specific**
```
❌ BAD: "remove stuff"
✅ GOOD: "remove all tables"
✅ GOOD: "delete the abstract section"
```

#### 2. **Include Action Verbs**
```
❌ BAD: "diabetes mentions"
✅ GOOD: "replace diabetes with type-2 diabetes"
✅ GOOD: "highlight diabetes in yellow"
```

#### 3. **Specify Target Details**
```
❌ BAD: "change something in the introduction"
✅ GOOD: "replace the word 'efficient' with 'effective' in the introduction"
✅ GOOD: "highlight the introduction section with yellow color"
```

#### 4. **Use Natural Language**
```
❌ BAD: "op:remove tgt:word val:dataset"
✅ GOOD: "remove the word dataset"
✅ GOOD: "I want to delete dataset mentions"
```

#### 5. **Be Explicit with Colors**
```
❌ BAD: "highlight this section"
✅ GOOD: "highlight the Methods section with yellow"
✅ GOOD: "highlight Introduction in blue color"
```

#### 6. **Specify Position for Additions**
```
❌ BAD: "add future work"
✅ GOOD: "add a Future Work section before Conclusion"
✅ GOOD: "insert new content after the introduction"
```

#### 7. **Include Exact Text for Specific Targets**
```
❌ BAD: "remove a sentence"
✅ GOOD: "remove this sentence: 'This is an old point.'"
✅ GOOD: "delete the sentence about limitations"
```

---

## Examples

### Remove Operations

#### Remove a Word
```
Prompt: "remove the word dataset"
Result: All occurrences of "dataset" removed
```

#### Remove All Tables
```
Prompt: "remove all tables"
Result: 6 tables removed (handles table, tabular, longtable environments)
```

#### Remove a Section
```
Prompt: "remove the related works section"
Result: Entire Related Works section deleted
```

#### Remove All Equations
```
Prompt: "remove all equations and formulas"
Result: 44 equations removed with math content validation
```

---

### Replace Operations

#### Replace a Word
```
Prompt: "replace the word diabetes with type-2 diabetes"
Result: All "diabetes" → "type-2 diabetes"
```

#### Replace Multiple Occurrences
```
Prompt: "replace 'machine learning' with 'neural networks' throughout the document"
Result: All instances replaced
```

---

### Add Operations

#### Add a Section
```
Prompt: "add a Future Work section before Conclusion with discussion about next steps"
Result: New "Future Work" section inserted before "Conclusion"
```

#### Add Content
```
Prompt: "add this text at the end: 'This concludes our study.'"
Result: Text appended to document
```

---

### Format Operations

#### Highlight a Word
```
Prompt: "highlight FluentNet with yellow color"
Result: All occurrences of "FluentNet" highlighted in yellow
```

#### Highlight a Section
```
Prompt: "highlight the introduction section with blue"
Result: Introduction section highlighted with blue background
```

#### Make Text Bold
```
Prompt: "make the word important bold"
Result: All "important" words formatted as bold
```

---

## API Endpoints

### 1. **Document Editing** 
```bash
POST /api/v1/edit/edit-doc-v1
Content-Type: application/json

{
  "file_id": "string",
  "prompt": "your natural language prompt here"
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "new_file_id",
  "operation": "remove|replace|add|format",
  "action": "remove_word|replace_phrase|...",
  "changes": 5,
  "processing_time": 3.45,
  "parsed_query": { ... },
  "message": "Document edited successfully"
}
```

---

### 2. **File Upload**
```bash
POST /api/v1/files/upload
Content-Type: multipart/form-data

file: <your_file.pdf or .tex>
```

**Response:**
```json
{
  "file_id": "unique_file_id",
  "filename": "your_file.pdf",
  "file_size": 512000,
  "upload_time": "2025-11-11T00:26:36",
  "message": "File uploaded successfully"
}
```

---

### 3. **RAG-Based LaTeX Fixing**
```bash
POST /api/v1/fix/latex-rag
Content-Type: application/json

{
  "file_id": "file_id",
  "document_type": "research",
  "conference": "IEEE",
  "column_format": "2-column",
  "converted": true,
  "original_format": "PDF",
  "compile_pdf": false
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "fixed_file_id",
  "issues_found": 62,
  "issues_fixed": 62,
  "processing_time": 55.65,
  "mathpix_metadata": {
    "conversion_method": "official_sdk_mpxpy",
    "main_file": "2025_11_10_xxxxx.tex",
    "images_extracted": 6
  },
  "message": "LaTeX document processed successfully"
}
```

---

### 4. **PDF Compilation**
```bash
POST /api/v1/compile/pdf
Content-Type: application/json

{
  "file_id": "file_id",
  "engine": "pdflatex"
}
```

**Response:**
```json
{
  "success": true,
  "pdf_id": "pdf_file_id",
  "compilation_time": 1.63,
  "log": "LaTeX compilation log...",
  "message": "LaTeX compiled successfully"
}
```

---

## File Management

### File Storage Structure
```
fastapi_backend/
├── downloads/          # Processed LaTeX files
├── uploads/           # Uploaded files
├── temp/              # Temporary processing
└── latex fixed output:input/  # RAG fixer output
```

### File ID Format
All files are assigned unique UUIDs (e.g., `378dad3c-bc7f-4bb9-abe5-d17bf88fda17`) for easy tracking.

### Supported File Formats
- **Input:** `.pdf`, `.tex`, `.latex`
- **Output:** `.pdf`, `.tex`

---

## Query Parser Intelligence

The system uses multi-layer parsing for robustness:

### Layer 1: AI-Powered Parsing
- Uses Gemini 2.5 Flash AI model
- Understands natural language intent
- Extracts operation, action, target, and metadata

### Layer 2: Validation
- Validates operation type (remove, replace, add, format)
- Validates target type (word, phrase, sentence, section, table, equation)
- Ensures valid color selections
- Confidence scoring (0.0-1.0)

### Layer 3: Fallback Detection
- Keyword-based detection if AI parsing fails
- Handles edge cases like "remove all tables"
- Automatic target type detection

---

## Advanced Features

### Math Content Validation
When removing equations, the system validates that content is actually mathematical:

```python
Math indicators checked:
- LaTeX commands (\frac, \sqrt, etc.)
- Mathematical operators (^, _, =, etc.)
- Greek letters (\alpha, \beta, etc.)
- Math fonts (\mathbb, \mathcal, etc.)
```

**Example:**
```
Input: "$ Elizabeth Chun $"
Result: Skipped (not math content)

Input: "$\mathcal{D}=\left\{\mathbf{x}_{j}^{(i)}\right\}_{i, j}$"
Result: Removed (valid math content)
```

---

## Error Handling

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Invalid result from AI" | Unrecognized operation type | Use standard verbs: remove, replace, add, highlight |
| "File not found" | Wrong file ID | Verify file ID from upload response |
| "LaTeX compilation failed" | Malformed LaTeX structure | Check document syntax |
| "No changes made" | Ambiguous prompt | Be more specific with target text |

---

## Tips and Tricks

### ✅ Pro Tips

1. **Chain Operations**: Process files through multiple operations sequentially
   ```
   1. Upload PDF
   2. Apply RAG fixer
   3. Remove unwanted sections
   4. Highlight important terms
   5. Compile to PDF
   ```

2. **Specific Targeting**: Use exact phrases for precision
   ```
   GOOD: "remove the sentence: 'This is outdated.'"
   BETTER THAN: "remove the old sentence"
   ```

3. **Batch Operations**: Combine similar operations
   ```
   "remove all tables, equations, and the abstract section"
   ```

4. **Verification**: Always compile after edits
   ```
   After editing → Compile to verify no LaTeX errors
   ```

5. **Section Names**: Use exact section titles
   ```
   "remove the Introduction section" (exact match)
   NOT: "remove intro" (may not match)
   ```

---

## Example Workflows

### Workflow 1: PDF Processing Pipeline
```
1. Upload PDF
   curl -X POST /api/v1/files/upload -F "file=@document.pdf"
   → file_id: abc123

2. Apply RAG Fixer
   curl -X POST /api/v1/fix/latex-rag \
     -d '{"file_id":"abc123","converted":true,"original_format":"PDF"}'
   → file_id: def456

3. Remove Abstract
   curl -X POST /api/v1/edit/edit-doc-v1 \
     -d '{"file_id":"def456","prompt":"remove the abstract section"}'
   → file_id: ghi789

4. Compile to PDF
   curl -X POST /api/v1/compile/pdf \
     -d '{"file_id":"ghi789","engine":"pdflatex"}'
   → pdf_id: xyz999
```

### Workflow 2: Document Editing
```
1. Upload LaTeX file
   → file_id: file001

2. Highlight introduction
   prompt: "highlight the introduction section with yellow"
   → file_id: file002

3. Replace terminology
   prompt: "replace AI with Artificial Intelligence"
   → file_id: file003

4. Add future work
   prompt: "add a Future Work section before Conclusion"
   → file_id: file004

5. Remove all tables
   prompt: "remove all tables"
   → file_id: file005

6. Compile
   → PDF ready
```

---

## Performance Metrics

### Average Processing Times
- **Document Editing**: 3-15 seconds per operation
- **PDF Upload**: 2-5 seconds
- **Mathpix Conversion**: 40-60 seconds per PDF
- **RAG Fixer**: 30-60 seconds
- **PDF Compilation**: 1-5 seconds

### Supported Document Sizes
- **LaTeX Files**: Up to 50MB
- **PDF Files**: Up to 1GB
- **Images**: Unlimited (automatic optimization)

---

## Support & Troubleshooting

### Debug Mode
Enable detailed logging by checking server output:
```bash
# Monitor server logs
tail -f server.log
```

### Verify Installation
```bash
# Check API availability
curl http://localhost:8000/api/v1/health

# View API documentation
http://localhost:8000/docs
```

---

## Summary

The AI Document Editor provides powerful document processing with natural language commands. By following this guide and writing clear, specific prompts, you can efficiently:

✅ Remove content (words, phrases, sections, tables, equations)
✅ Replace and modify text
✅ Add new sections and content
✅ Format and highlight important information
✅ Convert PDFs to LaTeX
✅ Fix and optimize documents
✅ Compile final PDFs

**Remember:** Clear, natural language prompts yield better results. Be specific about what you want, include action verbs, and verify results with compilation.
