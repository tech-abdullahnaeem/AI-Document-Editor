# 🚀 Quick Setup & Testing Guide

## Prerequisites
- Python 3.8+
- Your Gemini API key

## Setup (5 minutes)

### 1. Configure API Keys
Edit `.env` file and set:
```bash
GEMINI_API_KEY=your-actual-gemini-api-key
FASTAPI_API_KEY=your-chosen-secret-key
```

### 2. Start the Server
```bash
cd fastapi_backend
./start.sh
```

The server will start at `http://localhost:8000`

### 3. Test the Workflow
In a new terminal:
```bash
cd fastapi_backend
python test_workflow.py ../test_normal_document.tex
```

## What You'll See

### Server Output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Test Output:
```
🚀 FASTAPI WORKFLOW TEST
============================================================

🔍 Testing health check...
Status: 200
✅ Health check passed

📤 Testing file upload...
✅ Uploaded: test_normal_document.tex
   File ID: abc-123-def

🔧 Testing LaTeX fixing (RAG)...
✅ Fixed successfully
   Issues found: 5
   Issues fixed: 5

✏️  Testing document editing...
   Prompt: 'make all tables bold'
✅ Edited successfully
   Edits applied: 3

📄 Testing PDF compilation...
✅ Compiled successfully
   PDF ID: xyz-789

💾 Testing file download...
✅ Downloaded: test_output.pdf

✅ WORKFLOW COMPLETE! Total time: 45.32s
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Main Workflow Endpoints

### 1. Upload LaTeX File
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "X-API-Key: your-secret-api-key" \
  -F "file=@document.tex"
```

### 2. Fix LaTeX (RAG)
```bash
curl -X POST "http://localhost:8000/api/v1/fix/latex-rag" \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc-123",
    "document_type": "research",
    "conference": "IEEE",
    "column_format": "2-column"
  }'
```

### 3. Edit with Prompt
```bash
curl -X POST "http://localhost:8000/api/v1/edit/prompt" \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc-123",
    "prompt": "make all section headers bold"
  }'
```

### 4. Compile to PDF
```bash
curl -X POST "http://localhost:8000/api/v1/compile/pdf" \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "abc-123",
    "engine": "pdflatex"
  }'
```

### 5. Download PDF
```bash
curl -X GET "http://localhost:8000/api/v1/files/download/pdf-456" \
  -H "X-API-Key: your-secret-api-key" \
  -o output.pdf
```

## Troubleshooting

### Server won't start
- Check `.env` file exists
- Verify Python 3.8+ installed: `python --version`
- Check port 8000 not in use: `lsof -i :8000`

### "Authentication required" error
- Make sure `X-API-Key` header matches `FASTAPI_API_KEY` in `.env`

### RAG fixer fails
- Verify `GEMINI_API_KEY` is set correctly in `.env`
- Check internet connection (API needs to reach Gemini)

### Compilation fails
- Ensure LaTeX is installed: `which pdflatex`
- macOS: Install MacTeX
- Linux: `sudo apt-get install texlive-full`

### Import errors
- Make sure you're in the parent directory structure
- RAG fixer and document editor must be accessible
- Run from the project root, not from inside fastapi_backend

## File Structure
```
Document agent-tagged copy 2/
├── fastapi_backend/          # FastAPI backend
│   ├── main.py              # Start here
│   ├── start.sh             # Easy startup script
│   ├── test_workflow.py     # Test the workflow
│   ├── .env                 # Your API keys (don't commit!)
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   └── uploads/             # Temporary file storage
├── Rag latex fixer final without img/  # RAG fixer code
└── src/doc_edit/            # Document editor code
```

## Next Steps

1. ✅ Start server: `./start.sh`
2. ✅ Run test: `python test_workflow.py ../test_normal_document.tex`
3. ✅ Open docs: http://localhost:8000/docs
4. ✅ Try your own LaTeX files

## Production Deployment

For production use:
- Change `FASTAPI_API_KEY` to strong random key
- Set `RELOAD=False` in `.env`
- Use nginx reverse proxy
- Enable HTTPS
- Set up proper logging
- Configure file cleanup schedule
- Monitor API usage and rate limiting

## Support

Need help? Check:
- Full docs: `README.md`
- API docs: http://localhost:8000/docs
- Error logs in terminal output
