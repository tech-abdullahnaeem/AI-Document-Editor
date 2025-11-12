"""
LaTeX compiler for converting LaTeX code to PDF.
"""

import os
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LaTeXCompiler:
    """Handles compilation of LaTeX code to PDF."""

    def __init__(self, latex_engine: str = "pdflatex"):
        """
        Initialize the LaTeX compiler.

        Args:
            latex_engine: LaTeX engine to use (pdflatex, xelatex, lualatex)
        """
        self.latex_engine = latex_engine
        self.available_engines = []
        self.missing_packages = set()
        self.validate_latex_installation()
        self._detect_available_engines()

    def validate_latex_installation(self) -> bool:
        """
        Check if LaTeX is installed and accessible.

        Returns:
            True if LaTeX is available, raises RuntimeError otherwise
        """
        try:
            result = subprocess.run(
                [self.latex_engine, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True
            else:
                raise RuntimeError(f"LaTeX engine '{self.latex_engine}' is not working properly")
        except FileNotFoundError:
            raise RuntimeError(
                f"LaTeX engine '{self.latex_engine}' not found. "
                "Please install a LaTeX distribution like MiKTeX or TeX Live."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX installation check timed out")
    
    def _detect_available_engines(self) -> None:
        """Detect all available LaTeX engines."""
        engines = ["pdflatex", "xelatex", "lualatex", "latex"]
        for engine in engines:
            if self._is_engine_available(engine):
                self.available_engines.append(engine)
        
        logger.info(f"Available LaTeX engines: {self.available_engines}")
    
    def get_compilation_info(self) -> Dict[str, Any]:
        """
        Get information about the LaTeX installation and compiler capabilities.
        
        Returns:
            Dictionary with compilation environment information
        """
        return {
            "primary_engine": self.latex_engine,
            "available_engines": self.available_engines,
            "missing_packages": list(self.missing_packages),
            "latex_installed": len(self.available_engines) > 0
        }
    
    def _analyze_compilation_errors(self, log_output: str) -> Dict[str, List[str]]:
        """
        Analyze compilation log for common errors and suggestions.
        
        Args:
            log_output: LaTeX compilation log
            
        Returns:
            Dictionary with categorized errors and suggestions
        """
        errors = {
            "missing_packages": [],
            "syntax_errors": [],
            "font_errors": [],
            "reference_errors": [],
            "general_errors": [],
            "suggestions": []
        }
        
        lines = log_output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Missing package detection
            if "! LaTeX Error: File" in line and "not found" in line:
                package_match = re.search(r"File `([^']+)\.sty' not found", line)
                if package_match:
                    package = package_match.group(1)
                    errors["missing_packages"].append(package)
                    self.missing_packages.add(package)
                    errors["suggestions"].append(f"Install package: {package}")
            
            # Font errors
            elif "Font" in line and ("not found" in line or "unavailable" in line):
                errors["font_errors"].append(line)
                errors["suggestions"].append("Try using xelatex or lualatex for better font support")
            
            # Reference errors
            elif "Reference" in line and "undefined" in line:
                errors["reference_errors"].append(line)
                errors["suggestions"].append("Run LaTeX multiple times to resolve references")
            
            # Syntax errors
            elif "! " in line and any(keyword in line.lower() for keyword in 
                                   ["undefined control sequence", "missing", "extra", "misplaced"]):
                errors["syntax_errors"].append(line)
            
            # General errors
            elif line.startswith("! "):
                errors["general_errors"].append(line)
        
        return errors
    
    def _attempt_package_installation(self, package: str) -> bool:
        """
        Attempt to automatically install missing LaTeX packages.
        
        Args:
            package: Package name to install
            
        Returns:
            True if installation was attempted, False otherwise
        """
        # This is a basic implementation - in practice, package installation
        # varies greatly between LaTeX distributions
        try:
            # Try MiKTeX package manager
            result = subprocess.run(
                ["mpm", "--install", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info(f"Successfully installed package: {package}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            # Try TeX Live package manager
            result = subprocess.run(
                ["tlmgr", "install", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info(f"Successfully installed package: {package}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        logger.warning(f"Could not automatically install package: {package}")
        return False

    def compile_latex_to_pdf(
        self,
        latex_code: str,
        output_path: Optional[str] = None,
        working_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Compile LaTeX code to PDF.

        Args:
            latex_code: The LaTeX code to compile
            output_path: Path where to save the PDF (optional)
            working_dir: Working directory for compilation (optional)

        Returns:
            Tuple of (pdf_path, compilation_log)
        """
        if working_dir is None:
            working_dir = tempfile.mkdtemp()
            cleanup_temp = True
        else:
            cleanup_temp = False

        try:
            # Create temporary LaTeX file
            tex_file = os.path.join(working_dir, "document.tex")
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)

            # Copy images to working directory if they exist and are referenced
            self._copy_referenced_images(latex_code, working_dir, output_path)

            # Compile LaTeX
            pdf_path, log = self._run_latex_compilation(tex_file, working_dir)

            # Move PDF to desired location if specified
            if output_path:
                final_pdf_path = Path(output_path)
                final_pdf_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pdf_path, final_pdf_path)
                pdf_path = str(final_pdf_path)

            return pdf_path, log

        finally:
            if cleanup_temp and os.path.exists(working_dir):
                shutil.rmtree(working_dir, ignore_errors=True)

    def _run_latex_compilation(self, tex_file: str, working_dir: str) -> Tuple[str, str]:
        """
        Run the actual LaTeX compilation process.

        Args:
            tex_file: Path to the .tex file
            working_dir: Working directory for compilation

        Returns:
            Tuple of (pdf_path, compilation_log)
        """
        compilation_log = []
        pdf_path = tex_file.replace('.tex', '.pdf')

        # Try multiple engines if the primary fails
        engines_to_try = [self.latex_engine]
        if self.latex_engine == "pdflatex":
            engines_to_try.extend(["xelatex", "lualatex"])
        elif self.latex_engine == "xelatex":
            engines_to_try.extend(["lualatex", "pdflatex"])
        elif self.latex_engine == "lualatex":
            engines_to_try.extend(["xelatex", "pdflatex"])

        last_error = None

        for engine in engines_to_try:
            try:
                # Check if engine is available
                if not self._is_engine_available(engine):
                    compilation_log.append(f"Engine {engine} not available, skipping...")
                    continue

                compilation_log.append(f"\n=== Trying engine: {engine} ===")

                # Run compilation (usually twice for proper references)
                success = True
                for run_number in range(2):
                    try:
                        tex_filename = os.path.basename(tex_file) if working_dir and os.path.dirname(tex_file) == working_dir else tex_file

                        cmd_args = [
                            engine,
                            "-interaction=nonstopmode",
                            "-output-directory", working_dir,
                            tex_filename
                        ]

                        result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=working_dir, timeout=120, encoding='utf-8', errors='replace')

                        compilation_log.append(f"Run {run_number + 1} with {engine}:")
                        compilation_log.append(result.stdout)
                        if result.stderr:
                            compilation_log.append("STDERR:")
                            compilation_log.append(result.stderr)

                        if result.returncode != 0:
                            error_msg = f"LaTeX compilation failed on run {run_number + 1} with {engine}"
                            compilation_log.append(f"ERROR: {error_msg}")
                            success = False
                            break

                    except subprocess.TimeoutExpired:
                        compilation_log.append(f"ERROR: {engine} compilation timed out after 120 seconds")
                        success = False
                        break

                # Analyze compilation results
                full_log = "\n".join(compilation_log)
                error_analysis = self._analyze_compilation_errors(full_log)
                
                # Check if PDF was generated successfully
                if success and os.path.exists(pdf_path):
                    compilation_log.append(f"SUCCESS: PDF generated successfully with {engine}")
                    
                    # Add helpful information about any warnings
                    if error_analysis["suggestions"]:
                        compilation_log.append("SUGGESTIONS for future compilations:")
                        for suggestion in error_analysis["suggestions"]:
                            compilation_log.append(f"  - {suggestion}")
                    
                    return pdf_path, "\n".join(compilation_log)
                elif os.path.exists(pdf_path):
                    # Sometimes PDF is generated even with errors
                    compilation_log.append(f"WARNING: PDF generated with errors using {engine}")
                    
                    # Add error analysis
                    if error_analysis["missing_packages"]:
                        compilation_log.append(f"Missing packages: {', '.join(error_analysis['missing_packages'])}")
                    if error_analysis["suggestions"]:
                        compilation_log.append("Suggestions:")
                        for suggestion in error_analysis["suggestions"]:
                            compilation_log.append(f"  - {suggestion}")
                    
                    return pdf_path, "\n".join(compilation_log)
                else:
                    compilation_log.append(f"FAILED: No PDF generated with {engine}")
                    
                    # Add detailed error analysis for failed compilation
                    if error_analysis["missing_packages"]:
                        compilation_log.append(f"Missing packages detected: {', '.join(error_analysis['missing_packages'])}")
                        # Try to install missing packages
                        for package in error_analysis["missing_packages"]:
                            if self._attempt_package_installation(package):
                                compilation_log.append(f"Attempted to install: {package}")
                    
                    if error_analysis["suggestions"]:
                        compilation_log.append("Troubleshooting suggestions:")
                        for suggestion in error_analysis["suggestions"]:
                            compilation_log.append(f"  - {suggestion}")

            except Exception as e:
                last_error = str(e)
                compilation_log.append(f"EXCEPTION with {engine}: {str(e)}")
                continue

        # If we get here, all engines failed
        error_msg = f"All LaTeX engines failed. Last error: {last_error}"
        compilation_log.append(f"FINAL ERROR: {error_msg}")
        raise RuntimeError(f"{error_msg}. See compilation log for details.")

    def _is_engine_available(self, engine: str) -> bool:
        """
        Check if a LaTeX engine is available.

        Args:
            engine: LaTeX engine name

        Returns:
            True if engine is available, False otherwise
        """
        try:
            result = subprocess.run(
                [engine, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def test_compilation(self) -> Dict[str, Any]:
        """
        Test LaTeX compilation with a simple document.
        
        Returns:
            Dictionary with test results and system information
        """
        test_latex = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
\title{Test Document}
\author{LaTeX Compiler Test}
\date{\today}
\maketitle
\section{Test Section}
This is a test document to verify LaTeX compilation is working properly.
\[E = mc^2\]
\end{document}
"""
        
        test_results = {
            "compilation_successful": False,
            "engines_tested": [],
            "errors": [],
            "compilation_info": self.get_compilation_info(),
            "test_log": ""
        }
        
        try:
            pdf_path, log = self.compile_latex_to_pdf(test_latex)
            test_results["compilation_successful"] = True
            test_results["test_log"] = log
            test_results["pdf_generated"] = os.path.exists(pdf_path)
            
            # Clean up test file
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                
        except Exception as e:
            test_results["errors"].append(str(e))
            test_results["test_log"] = str(e)
        
        return test_results

    def _copy_referenced_images(self, latex_code: str, working_dir: str, output_path: Optional[str]):
        """Copy images referenced in LaTeX to the working directory"""
        import re
        
        # Find all image references in the LaTeX
        image_patterns = [
            r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',
            r'\\includepdf(?:\[[^\]]*\])?\{([^}]+)\}'
        ]
        
        image_files = set()
        for pattern in image_patterns:
            matches = re.findall(pattern, latex_code)
            image_files.update(matches)
        
        if not image_files:
            return
        
        # Determine source directory (where images might be)
        source_dirs = []
        if output_path:
            output_dir = Path(output_path).parent
            source_dirs.append(output_dir)
            source_dirs.append(output_dir / "images")
        
        # Add common image directories
        source_dirs.extend([
            Path.cwd(),
            Path.cwd() / "images",
            Path("images")
        ])
        
        # Copy found images
        copied_count = 0
        for image_file in image_files:
            image_path = Path(image_file)
            
            # Skip if it's already an absolute path
            if image_path.is_absolute():
                continue
                
            # Try to find the image in source directories
            found = False
            for source_dir in source_dirs:
                if not source_dir.exists():
                    continue
                    
                # Try different extensions if no extension provided
                if not image_path.suffix:
                    for ext in ['.jpg', '.jpeg', '.png', '.pdf', '.eps']:
                        full_path = source_dir / f"{image_file}{ext}"
                        if full_path.exists():
                            self._copy_image_to_working_dir(full_path, working_dir, image_file + ext)
                            copied_count += 1
                            found = True
                            break
                else:
                    full_path = source_dir / image_file
                    if full_path.exists():
                        self._copy_image_to_working_dir(full_path, working_dir, image_file)
                        copied_count += 1
                        found = True
                        break
                        
                if found:
                    break
        
        if copied_count > 0:
            logger.info(f"Copied {copied_count} image files to compilation directory")
    
    def _copy_image_to_working_dir(self, source_path: Path, working_dir: str, target_name: str):
        """Copy a single image file to the working directory"""
        target_path = Path(working_dir) / target_name
        
        # Create subdirectories if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied image: {source_path} -> {target_path}")
        except Exception as e:
            logger.warning(f"Failed to copy image {source_path}: {e}")