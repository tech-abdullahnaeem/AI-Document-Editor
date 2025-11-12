# Document Editing Agent

A comprehensive AI-powered document editing agent that converts uploaded documents (PDF/Word) to LaTeX and allows natural language editing via Google Gemini API. Perfect for researchers, writers, and anyone who needs to edit documents using simple natural language instructions.

## 🌟 Features

- 🤖 **AI-Powered Natural Language Editing**: Use Google's Gemini models to edit documents with simple instructions
- 📄 **Tagged PDF Support**: Enhanced structure preservation for accessible PDFs
- 🔄 **Multi-Format Support**: Convert PDF, Word (.docx/.doc), and LaTeX documents
- 🌐 **Web Interface**: Beautiful drag-and-drop web interface for easy document editing
- 💻 **Command-Line Interface**: Powerful CLI for batch processing and automation
- 🐍 **Python API**: Programmatic access for integration into other applications
- 🛠️ **Comprehensive Editing**: Support for all types of document modifications

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your Gemini API key:**
   ```bash
   cp env_example.txt .env
   # Edit .env file and add your GEMINI_API_KEY
   ```

3. **Start the web application:**
   ```bash
   python start_web_app.py
   ```

4. **Open your browser** and go to `http://localhost:5000`

### Option 2: Command Line Interface

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Check system status:**
   ```bash
   doc-edit check
   ```

3. **Start editing documents:**
   ```bash
   # Edit a document
   doc-edit edit "document.pdf" "Make the title blue and add a new section about AI ethics"
   
   # Start web interface
   doc-edit web
   ```

## 📖 Comprehensive Editing Capabilities

The Document Editing Agent supports **ALL** types of document modifications through natural language:

### 📝 Text Modifications
- **Change Text**: "Change the title to 'Advanced AI Research'"
- **Add Text**: "Add a paragraph about machine learning after the introduction"
- **Remove Text**: "Remove the second paragraph in the conclusion"
- **Replace Text**: "Replace 'AI' with 'Artificial Intelligence' throughout the document"
- **Text Formatting**: "Make the first paragraph bold and italic"
- **Font Changes**: "Change the document font to Times New Roman"
- **Text Size**: "Make the title larger and the footnotes smaller"
- **Text Color**: "Change the headings to blue color"

### 🏗️ Section & Heading Management
- **Add Sections**: "Add a new section titled 'Methodology' after the introduction"
- **Remove Sections**: "Remove the 'Limitations' section"
- **Modify Headings**: "Change all subsections to regular sections"
- **Reorder Sections**: "Move the conclusion before the discussion"
- **Change Heading Levels**: "Make 'Results' a subsection under 'Analysis'"

### 🎨 Formatting & Layout
- **Text Alignment**: "Center-align the title and author information"
- **Page Layout**: "Change margins to 1.5 inches and add page numbers"
- **Spacing**: "Increase paragraph spacing and add line breaks"
- **Headers/Footers**: "Add a header with the document title"
- **Page Orientation**: "Change to landscape orientation for the last page"

### 📋 Lists & Tables
- **Create Lists**: "Convert the benefits paragraph into a bulleted list"
- **Modify Lists**: "Change the numbered list to bullets and add a new item"
- **Add Tables**: "Create a table comparing different algorithms with accuracy scores"
- **Edit Tables**: "Add a new column for 'Processing Time' to the existing table"
- **Table Formatting**: "Make the table header bold and center-aligned"

### 🧮 Mathematical Expressions
- **Add Equations**: "Add Einstein's E=mc² equation after the physics section"
- **Modify Formulas**: "Change the linear regression equation to include bias term"
- **Equation Formatting**: "Center-align all equations and number them"
- **Mathematical Notation**: "Add the quadratic formula with proper formatting"

### 🖼️ Advanced Features
- **Document Metadata**: "Change the author to 'Dr. Jane Smith' and update the date"
- **Cross-References**: "Add references between sections and equations"
- **Bibliography**: "Add a bibliography section with sample references"
- **Multi-column Layout**: "Make the abstract section two-column layout"

## 🔧 Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **LaTeX Distribution**:
   - **Windows**: [MiKTeX](https://miktex.org/)
   - **macOS**: [MacTeX](https://tug.org/mactex/)
   - **Linux**: `sudo apt-get install texlive-full`
3. **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Detailed Installation

```bash
# Clone or download the project
cd Document\ agent-tagged/

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env

# Edit .env file with your API key
nano .env  # or use any text editor

# Install the package (for CLI usage)
pip install -e .

# Test the installation
python start_web_app.py
```

## 💡 Usage Examples

### Web Interface Examples

1. **Upload a PDF**: Drag and drop or click to select your document
2. **Natural Language Editing**: Type instructions like:
   - "Make all headings blue and add a table of contents"
   - "Convert the methodology section into numbered steps"
   - "Add mathematical formulas for machine learning algorithms"
3. **Download Results**: Get both PDF and LaTeX source files

### Command Line Examples

```bash
# Basic document editing
doc-edit edit "research_paper.pdf" "Change the title to 'Deep Learning Survey' and make all section headings bold"

# Convert document to LaTeX only
doc-edit convert "document.docx" --output "converted_document"

# Edit existing LaTeX file
doc-edit edit-latex "paper.tex" "Add a new section about ethics in AI with subsections for bias and fairness"

# Create new document from scratch
doc-edit create "Create a research paper about quantum computing with sections for introduction, methodology, results, and conclusion"

# Start web interface
doc-edit web
```

### Python API Examples

```python
from doc_edit import DocumentEditor

# Initialize editor
editor = DocumentEditor()

# Edit a PDF document
result = editor.edit_document(
    document_path="research_paper.pdf",
    edit_prompt="Add a literature review section after the introduction with at least 5 recent papers",
    context="This is a machine learning research paper focusing on computer vision"
)

if result["success"]:
    print(f"✅ Edited PDF: {result['pdf_file']}")
    print(f"📄 LaTeX source: {result['tex_file']}")
else:
    print(f"❌ Error: {result['error']}")

# Convert document only
conversion_result = editor.convert_document("document.docx")

# Edit existing LaTeX
latex_result = editor.edit_latex_file(
    latex_path="paper.tex",
    edit_prompt="Make the abstract more concise and add keywords"
)

# Create new document
creation_result = editor.create_document(
    prompt="Create a technical report about renewable energy with charts and statistics"
)
```

## 🧪 Testing & Examples

### Run Comprehensive Examples

```bash
# Run all editing examples (requires Gemini API key)
cd examples/
python comprehensive_editing_examples.py

# Test basic functionality
python basic_usage.py
```

### Example Prompts to Try

**Text Modifications:**
- "Change the introduction to focus on deep learning instead of general AI"
- "Make all technical terms bold and add a glossary section"
- "Replace all instances of 'algorithm' with 'method'"

**Structure Changes:**
- "Add a methodology section with subsections for data collection and analysis"
- "Move the conclusion to the beginning as an executive summary"
- "Create a table of contents with page numbers"

**Formatting:**
- "Make the document use a two-column layout except for the title"
- "Change all headings to blue color and increase their font size"
- "Add page numbers in the footer and a header with the document title"

**Advanced Edits:**
- "Add a comparison table of different machine learning algorithms with accuracy metrics"
- "Insert mathematical formulas for linear regression and neural networks"
- "Create a bibliography section with 10 sample academic references"

## 🛠️ Configuration

### Environment Variables (.env file)

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
LATEX_ENGINE=pdflatex              # or xelatex, lualatex
DEFAULT_OUTPUT_DIR=output
GEMINI_MODEL=gemini-1.5-pro        # or gemini-1.5-flash
FLASK_ENV=development
```

### Supported File Formats

- **Input**: PDF, Word (.docx, .doc), LaTeX (.tex)
- **Output**: PDF, LaTeX (.tex)
- **Special Support**: Tagged PDFs with accessibility structure

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   CLI Interface  │    │   Python API    │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Document Editor       │
                    │   (Main Orchestrator)   │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Document       │    │ Gemini Client    │    │ LaTeX Compiler   │
│ Converter      │    │ (Natural Lang.   │    │ (PDF Generation) │
│ (PDF/Word→LaTeX)│    │  Processing)     │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

## 🔍 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Set your API key in the `.env` file
   - Ensure the `.env` file is in the project root

2. **"LaTeX engine not found"**
   - Install a LaTeX distribution (MiKTeX/TeX Live/MacTeX)
   - Ensure LaTeX binaries are in your system PATH

3. **"Upload failed" or "File not supported"**
   - Check file size (max 50MB)
   - Ensure file format is supported (PDF, DOCX, DOC, TEX)

4. **"Compilation failed"**
   - Check the compilation log for specific LaTeX errors
   - Try different LaTeX engines (pdflatex, xelatex, lualatex)

### Getting Help

```bash
# Check system status
doc-edit check

# View detailed logs
python start_web_app.py  # Shows detailed startup information

# Test with sample document
doc-edit edit "examples/sample.tex" "Make the title bold"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google** for providing the Gemini models for natural language processing
- **LaTeX Community** for the powerful typesetting system
- **Flask** for the web framework
- **PyMuPDF** for PDF processing capabilities

## 📞 Support

- 📧 **Issues**: Report bugs and feature requests via GitHub Issues
- 📖 **Documentation**: Check the examples and code comments
- 💬 **Community**: Join discussions in the project repository

---

**Ready to transform your document editing experience with AI? Get started today! 🚀**