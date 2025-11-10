# LaTeX Research Paper Templates

This directory contains clean, organized LaTeX templates for various academic conferences and journals.

## Template Structure

Each template folder contains:
- `template.tex` - Main LaTeX document template
- `references.bib` - Bibliography file with sample references
- Required class files (`.cls`) and style files (`.sty`)
- Sample figures (where applicable)

## Available Templates

### 1. ACM (ACM Conference/Journal Format)
**Files:**
- `template.tex` - ACM SIGPLAN format template
- `acmart.cls` - ACM article class
- `ACM-Reference-Format.bst` - Bibliography style
- Citation style files (`.bbx`, `.cbx`)
- `references.bib` - Sample bibliography

**Best for:** ACM conferences, ACM Transactions journals

### 2. IEEE_Conference (IEEE Conference Format)
**Files:**
- `template.tex` - IEEE conference paper template
- `IEEEtran.cls` - IEEE transaction class
- `references.bib` - Sample bibliography

**Best for:** IEEE conferences, IEEE workshops

### 3. IEEE_Journal (IEEE Journal Format)
**Files:**
- `template.tex` - IEEE journal paper template
- `references.bib` - Sample bibliography

**Best for:** IEEE Transactions journals, IEEE magazines

### 4. ICLR_Conference (ICLR Conference Format)
**Files:**
- `template.tex` - ICLR 2024 conference template
- `iclr2024_conference.sty` - ICLR style file
- `math_commands.tex` - Mathematical notation commands
- `figures/` - Sample figures directory
- `references.bib` - Sample bibliography
- Additional style files (`fancyhdr.sty`, `natbib.sty`)

**Best for:** ICLR conferences, similar ML/AI conferences

### 5. Interspeech_Conference (Interspeech Format)
**Files:**
- `template.tex` - Interspeech conference template
- `Interspeech.cls` - Interspeech class file
- `figure/` - Sample figures directory
- `references.bib` - Sample bibliography

**Best for:** Interspeech conferences, speech processing conferences

### 6. arXiv_Preprint (arXiv Preprint Format)
**Files:**
- `template.tex` - General article template for arXiv
- `src/` - Modular section files (abstract, intro, methods, etc.)
- `fig/` - Comprehensive figures directory
- `references.bib` - Sample bibliography

**Best for:** arXiv preprints, general academic papers

## Usage Guidelines

1. **Choose the appropriate template** based on your target venue
2. **Copy the entire template folder** to your working directory
3. **Rename and modify** `template.tex` for your paper
4. **Replace sample references** in `references.bib` with your citations
5. **Add your figures** to the figures directory
6. **Compile** using the appropriate LaTeX engine (pdflatex, xelatex, lualatex)

## Template Features

- ✅ Clean, minimal structure with only essential files
- ✅ Standardized naming convention (`template.tex`, `references.bib`)
- ✅ Sample bibliography entries for quick start
- ✅ Required class and style files included
- ✅ Sample figures where applicable
- ✅ Modular structure for complex documents (arXiv template)

## Notes

- All templates have been cleaned of research-specific content
- Compiled files (`.bbl`, `.aux`, etc.) have been removed
- Templates are ready for immediate use and customization
- Each template follows the official formatting guidelines of its respective venue