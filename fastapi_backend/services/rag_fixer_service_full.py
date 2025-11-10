"""
RAG LaTeX Fixer Service - FULL IMPLEMENTATION
Integrates with the enhanced_user_guided_rag module
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import tempfile
import shutil

# Import RAG modules using isolated import helper to avoid model conflicts
from .rag_import_helper import import_rag_modules

ContextAwareRAGFixer, DocumentContext, UserGuidedLaTeXProcessor, RAG_AVAILABLE = import_rag_modules()

# Import table fixer from a.py
# Add parent directory to path to import a.py
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))
try:
    from a import fix_latex_table_generic
    TABLE_FIXER_AVAILABLE = True
    print("✅ Table fixer (a.py) loaded successfully")
except ImportError as e:
    TABLE_FIXER_AVAILABLE = False
    print(f"⚠️  Table fixer (a.py) not available: {e}")


class RAGFixerService:
    """Service for RAG-based LaTeX fixing with full AI capabilities"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
        
        # Initialize RAG availability as None - will be checked on first use
        self._rag_available = None
        self._rag_components_loaded = False
    
    @property
    def rag_available(self):
        """Check RAG availability lazily on first access"""
        if self._rag_available is None:
            self._rag_available = self._check_rag_availability()
            print(f"🔍 RAG availability check result: {self._rag_available}")
        return self._rag_available
    
    def _check_rag_availability(self):
        """Check if RAG components can be loaded"""
        try:
            print("🔍 Checking RAG availability...")
            # Try to import RAG modules fresh each time
            result = import_rag_modules()
            available = result[3] if result else False
            print(f"🔍 RAG import result: {result}")
            print(f"🔍 RAG available: {available}")
            if not available:
                print("⚠️  RAG mode unavailable - using simplified mode")
            else:
                print("✅ RAG mode is available!")
            return available
        except Exception as e:
            print(f"⚠️  RAG mode unavailable ({e}) - using simplified mode")
            import traceback
            traceback.print_exc()
            return False
    
    async def fix_latex_document(
        self,
        latex_content: str,
        document_type: str = "research",
        conference: str = "IEEE",
        column_format: str = "2-column",
        converted: bool = False,
        original_format: Optional[str] = None,
        compile_pdf: bool = True,
        images_dir: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix LaTeX document using RAG approach
        
        Args:
            latex_content: LaTeX source code
            document_type: "research" or "normal"
            conference: Conference type (IEEE, ACM, SPRINGER, ELSEVIER, GENERIC)
            column_format: "1-column" or "2-column"
            converted: Whether document was converted from PDF
            original_format: Original document format (PDF or LATEX)
            compile_pdf: Whether to compile to PDF
            images_dir: Path to directory containing images (optional)
            
        Returns:
            Dictionary with fixed content and metadata
        """
        
        print(f"📋 fix_latex_document called with:")
        print(f"   - document_type: {document_type} (type: {type(document_type)})")
        print(f"   - conference: {conference}")
        print(f"   - column_format: {column_format}")
        print(f"   - file_path: {file_path}")
        print(f"   - rag_available: {self.rag_available} (checking...)")
        
        # ALWAYS use RAG for PDF files, regardless of document_type
        if file_path and Path(file_path).suffix.lower() == '.pdf':
            print(f"🎯 PDF file detected - FORCING RAG mode for PDF-to-LaTeX conversion")
            return await self._fix_with_rag(
                latex_content, document_type, conference, column_format, 
                converted, original_format, compile_pdf, images_dir, file_path
            )
        elif self.rag_available and document_type == "research":
            # Use full RAG implementation for research papers
            print(f"🎯 Using FULL RAG mode (rag_available={self.rag_available}, document_type={document_type})")
            return await self._fix_with_rag(
                latex_content, document_type, conference, column_format, 
                converted, original_format, compile_pdf, images_dir, file_path
            )
        else:
            # Use simplified fixes for normal documents or when RAG unavailable
            print(f"📝 Using SIMPLE mode (rag_available={self.rag_available}, document_type={document_type})")
            return await self._fix_simple(latex_content, compile_pdf)
    
    async def _fix_with_rag(
        self,
        latex_content: str,
        document_type: str,
        conference: str,
        column_format: str,
        converted: bool,
        original_format: Optional[str],
        compile_pdf: bool,
        images_dir: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix using full RAG implementation via subprocess execution
        Flow: 
        0. If PDF file detected, convert to LaTeX using MathPix
        1. First run a.py to fix tables (preprocess the content)
        2. Save preprocessed content to temp file
        3. Run user_guided_comprehensive_rag.py as subprocess with all enhancements:
           - RAG-based fixes
           - Image positioning ([!htbp])
           - Image size limiting (50% width)
           - Float parameters optimization
        4. Save all files (converted .tex, fixed .tex, PDF, images) to persistent output directory
        """
        
        # Initialize conversion tracking
        converted_from_pdf = False
        mathpix_metadata = None
        conversion_warnings = []
        
        try:
            # Create temporary working directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # STEP 0: Check if input is PDF and convert using MathPix
                # Always force PDF processing for debugging
                if file_path and Path(file_path).suffix.lower() == '.pdf':
                    print("📄 PDF file detected, converting to LaTeX using MathPix...")
                    
                    # Load environment variables before importing
                    from dotenv import load_dotenv
                    import os
                    load_dotenv()
                    
                    # Verify MathPix credentials are available
                    mathpix_app_id = os.getenv("MATHPIX_APP_ID")
                    mathpix_app_key = os.getenv("MATHPIX_APP_KEY")
                    print(f"🔑 MathPix credentials check: APP_ID={'✅ Found' if mathpix_app_id else '❌ Missing'}, APP_KEY={'✅ Found' if mathpix_app_key else '❌ Missing'}")
                    
                    try:
                        from .mathpix_service import MathPixService
                        
                        # Pass credentials explicitly
                        mathpix_service = MathPixService(app_id=mathpix_app_id, app_key=mathpix_app_key)
                        conversion_result = await mathpix_service.convert_pdf_to_latex(file_path)
                        
                        if conversion_result["success"]:
                            print("✅ MathPix conversion SUCCESS")
                            latex_content = conversion_result["latex_content"]
                            converted_from_pdf = True
                            mathpix_metadata = conversion_result.get("mathpix_metadata", {})
                            conversion_warnings = conversion_result.get("warnings", [])
                            
                            # Save converted LaTeX to persistent output directory
                            output_base = parent_dir / "latex fixed output:input"
                            output_base.mkdir(exist_ok=True)
                            converted_tex_file = output_base / f"{Path(file_path).stem}_converted.tex"
                            with open(converted_tex_file, 'w', encoding='utf-8') as f:
                                f.write(latex_content)
                            print(f"💾 Converted LaTeX saved to: {converted_tex_file}")
                            
                            # Extract and save images from MathPix ZIP
                            extracted_files = conversion_result.get("extracted_files", {})
                            file_structure = conversion_result.get("file_structure", {})
                            images_saved = 0
                            mathpix_images_dir = None
                            
                            if extracted_files:
                                print(f"📦 Processing {len(extracted_files)} extracted files...")
                                
                                # Create images directory for MathPix images
                                mathpix_images_dir = output_base / "images"
                                mathpix_images_dir.mkdir(exist_ok=True)
                                
                                # Save all extracted files
                                for file_name, file_data in extracted_files.items():
                                    try:
                                        # Determine save path
                                        if file_data['type'] == 'binary' and any(file_name.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.eps']):
                                            # Save images to images directory
                                            save_path = mathpix_images_dir / file_name
                                            save_path.parent.mkdir(parents=True, exist_ok=True)
                                            with open(save_path, 'wb') as f:
                                                f.write(file_data['content'])
                                            images_saved += 1
                                            print(f"🖼️  Saved image: {save_path}")
                                        elif file_data['type'] == 'text' and not file_name.endswith('.tex'):
                                            # Save other text files (bib, sty, etc.) to main directory
                                            save_path = output_base / file_name
                                            save_path.parent.mkdir(parents=True, exist_ok=True)
                                            with open(save_path, 'w', encoding='utf-8') as f:
                                                f.write(file_data['content'])
                                            print(f"📄 Saved file: {save_path}")
                                    except Exception as e:
                                        print(f"⚠️  Failed to save {file_name}: {e}")
                                
                                total_images = len(file_structure.get("image_files", []))
                                print(f"🖼️  Saved {images_saved}/{total_images} images to: {mathpix_images_dir}")
                                
                                # Update mathpix_metadata with extraction info
                                mathpix_metadata.update({
                                    "images_extracted": images_saved,
                                    "total_files_extracted": len(extracted_files),
                                    "images_directory": str(mathpix_images_dir)
                                })
                                
                                # Set images_dir for RAG processing to use MathPix images
                                if images_saved > 0:
                                    images_dir = str(mathpix_images_dir)
                                    print(f"🖼️  Setting images_dir for RAG processing: {images_dir}")
                            
                        else:
                            error_msg = f"MathPix conversion failed: {conversion_result.get('error', 'Unknown error')}"
                            print(f"❌ {error_msg}")
                            raise Exception(error_msg)
                            
                    except Exception as e:
                        error_msg = f"MathPix API failed: {str(e)}"
                        print(f"❌ {error_msg}")
                        raise Exception(error_msg)
                
                # STEP 1: Fix tables using a.py
                table_fixes_applied = False
                preprocessed_content = latex_content
                if TABLE_FIXER_AVAILABLE:
                    try:
                        print("🔧 STEP 1: Fixing tables with a.py...")
                        preprocessed_content = fix_latex_table_generic(latex_content)
                        table_fixes_applied = True
                        print("✅ Table fixes applied successfully")
                    except Exception as e:
                        print(f"⚠️  Table fixer error (continuing anyway): {e}")
                else:
                    print("⚠️  Table fixer not available, skipping table fixes")
                
                # Save preprocessed content to temp file
                input_file = temp_dir_path / "input.tex"
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(preprocessed_content)
                print(f"💾 Saved preprocessed content to: {input_file}")
                
                # Copy images to temp directory if provided
                if images_dir and os.path.exists(images_dir):
                    print(f"📸 Copying images from {images_dir}...")
                    images_source = Path(images_dir)
                    image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg', '.gif', '.bmp'}
                    copied_count = 0
                    
                    # Copy images maintaining directory structure
                    for img_file in images_source.rglob('*'):
                        if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                            # Maintain relative path structure
                            rel_path = img_file.relative_to(images_source)
                            dest_file = temp_dir_path / rel_path
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(img_file, dest_file)
                            copied_count += 1
                    
                    print(f"   ✅ Copied {copied_count} image files to temp directory")
                
                # STEP 2: Run comprehensive RAG fixer as subprocess
                print("🤖 STEP 2: Running comprehensive RAG fixer...")
                
                # Build command for user_guided_comprehensive_rag.py
                rag_script = parent_dir / "Rag latex fixer" / "user_guided_comprehensive_rag.py"
                
                cmd = [
                    sys.executable,  # Use same Python interpreter
                    str(rag_script),
                    "--file", str(input_file),
                    "--document-type", document_type,
                    "--conference", conference,
                    "--format", column_format,
                    "--output-dir", str(temp_dir_path / "output"),
                    "--test-name", "fastapi_fixed"
                ]
                
                if converted:
                    cmd.append("--converted")
                
                if original_format:
                    cmd.extend(["--original", original_format])
                
                if compile_pdf:
                    cmd.append("--compile-pdf")
                
                # Note: Images are already copied to temp directory, no need for --images-dir argument
                # The RAG processor will find them in the same directory as the LaTeX file
                
                print(f"📝 Command: {' '.join(cmd)}")
                
                # Set environment variable for Gemini API
                # Re-import os to ensure it's available (in case it was affected by RAG imports)
                import os as os_module
                env = os_module.environ.copy()
                env['GOOGLE_API_KEY'] = self.gemini_api_key
                
                # Run the RAG processor
                result = subprocess.run(
                    cmd,
                    cwd=str(parent_dir),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                print(f"📤 RAG processor output:")
                print(result.stdout)
                
                if result.returncode != 0:
                    print(f"⚠️  RAG processor stderr:")
                    print(result.stderr)
                    raise Exception(f"RAG processor failed with code {result.returncode}")
                
                # Read the fixed LaTeX file
                output_dir = temp_dir_path / "output"
                fixed_file = output_dir / "fastapi_fixed.tex"
                
                if not fixed_file.exists():
                    raise Exception(f"Fixed file not found: {fixed_file}")
                
                with open(fixed_file, 'r', encoding='utf-8') as f:
                    fixed_content = f.read()
                
                print(f"✅ Read fixed content ({len(fixed_content)} bytes)")
                
                # Read PDF if it was compiled
                pdf_content = None
                pdf_file = output_dir / "fastapi_fixed.pdf"
                if compile_pdf and pdf_file.exists():
                    with open(pdf_file, 'rb') as f:
                        pdf_content = f.read()
                    print(f"✅ Read compiled PDF ({len(pdf_content)} bytes)")
                
                # Parse output for statistics
                issues_found = 0
                issues_fixed = 0
                
                # Extract statistics from stdout
                for line in result.stdout.split('\n'):
                    if 'issues detected' in line.lower():
                        try:
                            issues_found = int(line.split()[0])
                        except:
                            pass
                    if 'fixes applied' in line.lower() or 'fixed' in line.lower():
                        try:
                            issues_fixed = int(line.split()[0])
                        except:
                            pass
                
                # STEP 4: Copy all output files to persistent directory
                output_base = parent_dir / "latex fixed output:input"
                output_base.mkdir(exist_ok=True)
                
                # Copy fixed LaTeX file
                final_tex_file = output_base / f"{conference}_{column_format.replace('-', '')}_fixed.tex"
                shutil.copy2(fixed_file, final_tex_file)
                print(f"💾 Fixed LaTeX saved to: {final_tex_file}")
                
                # Copy PDF if exists
                if pdf_file.exists():
                    final_pdf_file = output_base / f"{conference}_{column_format.replace('-', '')}_fixed.pdf"
                    shutil.copy2(pdf_file, final_pdf_file)
                    print(f"💾 PDF saved to: {final_pdf_file}")
                
                # Copy all images from temp directory to output directory
                image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg', '.gif', '.bmp'}
                images_copied = 0
                for img_file in temp_dir_path.rglob('*'):
                    if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                        dest_img = output_base / img_file.name
                        shutil.copy2(img_file, dest_img)
                        images_copied += 1
                print(f"📸 Copied {images_copied} images to output directory")
                
                # Save processing report
                report_file = output_base / f"{conference}_{column_format.replace('-', '')}_report.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(f"LaTeX Fixing Report\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"Conference: {conference}\n")
                    f.write(f"Column Format: {column_format}\n")
                    f.write(f"Document Type: {document_type}\n")
                    f.write(f"Converted from PDF: {converted_from_pdf}\n")
                    if converted_from_pdf:
                        f.write(f"MathPix Conversion: SUCCESS\n")
                    f.write(f"\nIssues Found: {issues_found}\n")
                    f.write(f"Issues Fixed: {issues_fixed}\n")
                    f.write(f"Table Fixes Applied: {table_fixes_applied}\n")
                    f.write(f"Images Copied: {images_copied}\n")
                    f.write(f"\nSubprocess Output:\n{'-' * 50}\n")
                    f.write(result.stdout)
                print(f"📄 Report saved to: {report_file}")
                
                # Print RAG processing result
                if result.returncode == 0:
                    print(f"✅ RAG processing SUCCESS - Fixed document ready")
                else:
                    print(f"⚠️  RAG processing completed with warnings")
                
                return {
                    "fixed_content": fixed_content,
                    "pdf_path": str(pdf_file) if pdf_file.exists() else None,
                    "pdf_content": pdf_content,
                    "issues_found": issues_found,
                    "issues_fixed": issues_fixed,
                    "images_copied": images_copied,
                    "output_directory": str(output_base),
                    "converted_from_pdf": converted_from_pdf,
                    "mathpix_metadata": mathpix_metadata,
                    "conversion_warnings": conversion_warnings,
                    "annotated_content": None,
                    "report": {
                        "total_issues": issues_found,
                        "fixes_applied": issues_fixed,
                        "table_fixes_applied": table_fixes_applied,
                        "document_type": "research",
                        "conference": conference,
                        "column_format": column_format,
                        "rag_mode": "full_subprocess",
                        "processing_steps": [
                            "1. Table fixes (a.py)" if table_fixes_applied else "1. Table fixes (skipped)",
                            "2. RAG-based comprehensive fixes (subprocess)",
                            "3. Image positioning ([!htbp])",
                            "4. Image size limiting (50% width)",
                            "5. Float parameters optimization",
                            "6. PDF compilation" if compile_pdf else "6. PDF compilation (skipped)"
                        ],
                        "subprocess_output": result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout  # Last 1000 chars
                    }
                }
                
        except subprocess.TimeoutExpired:
            print(f"❌ RAG processor timeout after 5 minutes")
            return await self._fix_simple(latex_content, compile_pdf)
        except Exception as e:
            print(f"❌ RAG processing error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple mode
            return await self._fix_simple(latex_content, compile_pdf)
    
    async def _fix_simple(
        self,
        latex_content: str,
        compile_pdf: bool = False
    ) -> Dict[str, Any]:
        """Simple LaTeX fixing without RAG"""
        
        fixed_content = latex_content
        fixes_applied = []
        
        # Apply basic LaTeX fixes
        
        # Fix 1: Add missing graphicx package
        if "\\usepackage{graphicx}" not in fixed_content and "\\includegraphics" in fixed_content:
            # Find a good place to add it (after other usepackage statements)
            if "\\usepackage{amsfonts}" in fixed_content:
                fixed_content = fixed_content.replace(
                    "\\usepackage{amsfonts}",
                    "\\usepackage{amsfonts}\n\\usepackage{graphicx}"
                )
            else:
                fixed_content = fixed_content.replace(
                    "\\begin{document}",
                    "\\usepackage{graphicx}\n\\begin{document}"
                )
            fixes_applied.append("Added missing graphicx package")
        
        # Fix 2: Fix double line breaks
        if "\\\\\\\\" in fixed_content:
            fixed_content = fixed_content.replace("\\\\\\\\", "\\\\")
            fixes_applied.append("Fixed double line breaks")
        
        # Fix 3: Fix empty citations
        if "\\cite{}" in fixed_content:
            fixed_content = fixed_content.replace("\\cite{}", "\\cite{reference}")
            fixes_applied.append("Fixed empty citations")
        
        # Fix 4: Add missing \n before \end{document}
        if "\\end{document}" in fixed_content:
            fixed_content = fixed_content.replace("\\end{document}", "\n\\end{document}")
        
        # Fix 5: Ensure hyperref is loaded last
        if "\\usepackage{hyperref}" in fixed_content:
            lines = fixed_content.split('\n')
            hyperref_line = None
            hyperref_idx = -1
            
            for i, line in enumerate(lines):
                if "\\usepackage{hyperref}" in line or "\\usepackage[" in line and "hyperref" in line:
                    hyperref_line = line
                    hyperref_idx = i
                    break
            
            if hyperref_idx != -1 and hyperref_idx < len(lines) - 5:
                # Check if there are other usepackage statements after hyperref
                has_packages_after = any("\\usepackage" in lines[i] for i in range(hyperref_idx + 1, len(lines)) if i < len(lines) and "\\begin{document}" not in lines[i])
                
                if has_packages_after:
                    lines.pop(hyperref_idx)
                    # Find the last usepackage before \begin{document}
                    last_package_idx = hyperref_idx
                    for i in range(hyperref_idx, len(lines)):
                        if "\\begin{document}" in lines[i]:
                            break
                        if "\\usepackage" in lines[i]:
                            last_package_idx = i
                    
                    lines.insert(last_package_idx + 1, hyperref_line)
                    fixed_content = '\n'.join(lines)
                    fixes_applied.append("Moved hyperref package to load last")
        
        return {
            "fixed_content": fixed_content,
            "pdf_path": None,
            "issues_found": len(fixes_applied),
            "issues_fixed": len(fixes_applied),
            "report": {
                "total_issues": len(fixes_applied),
                "contextual_fixes": 0,
                "generic_fixes": len(fixes_applied),
                "confidence_scores": [],
                "document_type": "normal",
                "conference": "GENERIC",
                "column_format": "1-column",
                "fixes_applied": fixes_applied,
                "rag_mode": "simple"
            }
        }
    
    async def fix_latex_simple(
        self,
        latex_content: str,
        document_type: str = "normal",
        compile_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Simple LaTeX fixing without RAG (faster, basic fixes)
        """
        return await self._fix_simple(latex_content, compile_pdf)
    
    def _generate_annotated_latex(self, original_content: str, fixes: List[Dict]) -> str:
        """
        Generate annotated LaTeX showing where fixes were applied
        
        Args:
            original_content: Original LaTeX content
            fixes: List of fixes with issue and fix information
            
        Returns:
            Annotated LaTeX content with comments
        """
        annotated = original_content
        
        # Add header comment
        header = """% ========================================
% ANNOTATED LATEX - RAG FIXES APPLIED
% ========================================
% This file shows where AI-powered fixes were applied
% Generated by RAG LaTeX Fixer with full context awareness
%
"""
        annotated = header + annotated
        
        # Add annotations for each fix
        for i, fix_info in enumerate(fixes, 1):
            issue = fix_info['issue']
            fix = fix_info['fix']
            
            # Create annotation comment
            annotation = f"""
% ----------------------------------------
% FIX #{i}: {issue.get('description', 'Unknown issue')}
% Type: {issue.get('type', 'Unknown')}
% Priority: {issue.get('context_priority', 'MEDIUM')}
% Confidence: {fix.get('confidence', 0.0):.2f}
% Line: {issue.get('line_number', 'Unknown')}
% ----------------------------------------
"""
            
            # Try to insert annotation near the fix location
            # This is a simplified version - could be enhanced
            annotated += annotation
        
        # Add footer
        footer = f"""
% ========================================
% END OF ANNOTATIONS
% Total fixes applied: {len(fixes)}
% ========================================
"""
        annotated += footer
        
        return annotated
    
    def _generate_detailed_report(
        self,
        processed_fixes: List[Dict],
        original_size: int,
        fixed_size: int,
        conference: str,
        column_format: str,
        context: Any
    ) -> Dict[str, Any]:
        """
        Generate detailed JSON report of fixes
        
        Args:
            processed_fixes: List of processed fixes
            original_size: Size of original content
            fixed_size: Size of fixed content
            conference: Conference type
            column_format: Column format
            context: Document context
            
        Returns:
            Detailed report dictionary
        """
        # Calculate statistics
        confidence_scores = [fix['fix'].get('confidence', 0.0) for fix in processed_fixes]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Count contextual vs generic fixes
        contextual_count = sum(1 for fix in processed_fixes if fix.get('is_contextual', False))
        generic_count = len(processed_fixes) - contextual_count
        
        # Categorize fixes by type
        fix_types = {}
        for fix_info in processed_fixes:
            fix_type = fix_info['issue'].get('type', 'unknown')
            fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
        
        # Build detailed fixes list
        detailed_fixes = []
        for i, fix_info in enumerate(processed_fixes, 1):
            issue = fix_info['issue']
            fix = fix_info['fix']
            
            detailed_fixes.append({
                "fix_number": i,
                "issue": {
                    "type": issue.get('type', 'Unknown'),
                    "description": issue.get('description', ''),
                    "severity": issue.get('severity', 'MEDIUM'),
                    "line_number": issue.get('line_number', 0),
                    "priority": issue.get('context_priority', 'MEDIUM')
                },
                "fix": {
                    "confidence": fix.get('confidence', 0.0),
                    "context_relevance": fix.get('context_relevance', 'Unknown'),
                    "explanation": fix.get('explanation', ''),
                    "fix_content": fix.get('fix', '')[:200]  # Truncate long fixes
                },
                "is_contextual": fix_info.get('is_contextual', False)
            })
        
        # Build complete report
        report = {
            "summary": {
                "total_issues": len(processed_fixes),
                "contextual_fixes": contextual_count,
                "generic_fixes": generic_count,
                "average_confidence": avg_confidence,
                "original_size": original_size,
                "fixed_size": fixed_size,
                "size_change": fixed_size - original_size
            },
            "document_context": {
                "conference_type": conference,
                "column_format": column_format,
                "original_format": getattr(context, 'original_format', None),
                "conversion_applied": getattr(context, 'conversion_applied', False)
            },
            "fix_categories": fix_types,
            "fixes": detailed_fixes
        }
        
        return report