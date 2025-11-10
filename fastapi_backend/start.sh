#!/bin/bash

# FastAPI Backend Startup Script

echo "🚀 Starting FastAPI Backend"
echo "================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - FASTAPI_API_KEY"
    echo "   - GEMINI_API_KEY"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if API keys are set
source .env
if [ "$GEMINI_API_KEY" == "your-gemini-api-key-here" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set in .env file"
    echo "   The RAG fixer and document editor will not work!"
fi

if [ "$FASTAPI_API_KEY" == "your-secret-api-key-change-this" ]; then
    echo "⚠️  WARNING: FASTAPI_API_KEY not changed from default"
    echo "   Please use a secure API key in production!"
fi

echo ""
echo "✅ Starting server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""

# Start the server
python main.py
