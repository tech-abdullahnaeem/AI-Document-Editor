# AI Document Editor — Frontend

This is a Vite + React + Tailwind frontend for the AI-powered LaTeX Document Editing API.

Features
- Three pages: AI Editor, Format Mapper, PDF → LaTeX Converter
- Upload and preview PDFs (react-pdf)
- Prompt-based editing and compilation
- Format mapping (RAG fixer)
- PDF → LaTeX conversion and .tex download

Quick start

1. cd into the frontend folder

```powershell
cd "d:\\final with fast api copy\\final with fast api copy\\frontend"
npm install
npm run dev
```

2. Open http://localhost:5173

Configuration
- To change the backend base URL set environment variable VITE_API_BASE. Example (PowerShell):

```powershell
$env:VITE_API_BASE = 'http://localhost:8000'; npm run dev
```

Notes
- The project uses `react-pdf` which requires the PDF.js worker route (configured automatically in the pages).
- The API service is in `src/services/api.js` and centralizes network calls. Adjust the base URL if needed.
