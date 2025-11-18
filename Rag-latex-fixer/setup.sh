#!/bin/bash
# Setup script for RAG LaTeX Fixer

echo "=================================================="
echo "RAG LaTeX Fixer - Setup Script"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3 not found"; exit 1; }
echo "✓ Python found"
echo ""

# Create virtual environment (optional but recommended)
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "To activate virtual environment, run:"
echo "  source venv/bin/activate  (on macOS/Linux)"
echo "  venv\\Scripts\\activate    (on Windows)"
echo ""
read -p "Press Enter to continue with installation..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || { echo "Error: Installation failed"; exit 1; }
echo "✓ Dependencies installed"
echo ""

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
else
    echo "✓ .env file already exists"
fi
echo ""

# Test installation
echo "Testing installation..."
python test_installation.py
echo ""

# Check for pdflatex (optional)
echo "Checking for pdflatex (optional, for validation)..."
if command -v pdflatex &> /dev/null; then
    echo "✓ pdflatex found - validation will work"
else
    echo "⚠️  pdflatex not found - use --no-validate flag"
    echo "   Install: brew install mactex (macOS) or apt-get install texlive (Linux)"
fi
echo ""

echo "=================================================="
echo "✓ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your GEMINI_API_KEY"
echo "  2. Run: python examples.py"
echo "  3. Try: python cli.py your_file.tex"
echo ""
echo "Documentation:"
echo "  - README.md - Full documentation"
echo "  - QUICKSTART.md - Quick start guide"
echo "  - examples.py - Usage examples"
echo ""
echo "Happy fixing! 🎉"
