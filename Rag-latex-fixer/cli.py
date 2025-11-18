"""
Command-line interface for RAG LaTeX Fixer
"""
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from loguru import logger

from pipeline import LatexFixerPipeline
from config import settings

console = Console()


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def main():
    parser = argparse.ArgumentParser(
        description="RAG-based LaTeX Style & Layout Fixer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix a LaTeX file for IEEE two-column format
  python cli.py input.tex -f IEEE_two_column -o output.tex
  
  # Fix without compilation validation (faster)
  python cli.py input.tex --no-validate
  
  # Show detailed report
  python cli.py input.tex --report
        """
    )
    
    parser.add_argument("input", type=Path, help="Input LaTeX file")
    parser.add_argument("-o", "--output", type=Path, help="Output file (default: input_fixed.tex)")
    parser.add_argument("-f", "--format", 
                       choices=settings.SUPPORTED_FORMATS,
                       default="IEEE_two_column",
                       help="Target document format (default: IEEE_two_column)")
    parser.add_argument("--no-validate", action="store_true",
                       help="Skip compilation validation")
    parser.add_argument("--report", action="store_true",
                       help="Show detailed fix report")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    # Check input file
    if not args.input.exists():
        console.print(f"[red]Error: Input file not found: {args.input}[/red]")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        output_file = args.input.parent / f"{args.input.stem}_fixed.tex"
    
    # Read input
    console.print(f"[cyan]Reading input file: {args.input}[/cyan]")
    latex_content = args.input.read_text(encoding='utf-8')
    
    # Initialize pipeline
    console.print(f"[cyan]Initializing RAG LaTeX Fixer for {args.format} format...[/cyan]")
    pipeline = LatexFixerPipeline()
    
    # Process
    with Progress() as progress:
        task = progress.add_task("[green]Processing document...", total=None)
        
        report = pipeline.process_document(
            latex_content,
            document_format=args.format,
            validate_compilation=not args.no_validate
        )
    
    # Display results
    if report.success:
        console.print(f"[green]✓ Successfully processed document![/green]")
        console.print(f"[green]  Fixed {len(report.issues_fixed)} issues in {report.processing_time:.2f}s[/green]")
    else:
        console.print(f"[yellow]⚠ Processing completed with warnings[/yellow]")
    
    # Show detailed report if requested
    if args.report:
        display_report(report)
    
    # Save output
    output_file.write_text(report.fixed_latex, encoding='utf-8')
    console.print(f"[cyan]Saved fixed document to: {output_file}[/cyan]")
    
    sys.exit(0 if report.success else 1)


def display_report(report):
    """Display detailed fix report"""
    
    # Issues table
    if report.issues_fixed:
        table = Table(title="Detected Issues", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Element", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Description")
        
        for issue in report.issues_fixed:
            table.add_row(
                issue.type.value,
                issue.element,
                issue.severity.value,
                issue.description
            )
        
        console.print(table)
    
    # Fixes applied
    if report.fixes_applied:
        console.print("\n[bold]Fixes Applied:[/bold]")
        for i, fix in enumerate(report.fixes_applied, 1):
            panel_content = f"""
[yellow]Changes:[/yellow]
{chr(10).join('• ' + change for change in fix.changes_made)}

[yellow]Confidence:[/yellow] {fix.confidence_score:.1%}

[yellow]Retrieved Examples:[/yellow] {len(fix.retrieved_examples)} examples used
            """
            console.print(Panel(panel_content, title=f"Fix {i}", border_style="green"))
    
    # Validation
    if report.validation_result:
        val = report.validation_result
        status = "✓ Passed" if val.compilation_success else "✗ Failed"
        style = "green" if val.compilation_success else "red"
        
        console.print(f"\n[{style}]Validation: {status}[/{style}]")
        console.print(f"Style Compliance Score: {val.style_compliance_score:.1%}")
        
        if val.improvements:
            console.print("[green]Improvements:[/green]")
            for imp in val.improvements:
                console.print(f"  • {imp}")
        
        if val.warnings:
            console.print("[yellow]Warnings:[/yellow]")
            for warn in val.warnings:
                console.print(f"  • {warn}")


if __name__ == "__main__":
    main()
