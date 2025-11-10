"""
PDF to LaTeX Converter Router - MathPix integration (NOT IMPLEMENTED YET)
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import PDFToLatexRequest, PDFToLatexResponse

router = APIRouter()

@router.post("/pdf-to-latex", response_model=PDFToLatexResponse)
async def convert_pdf_to_latex(request: PDFToLatexRequest):
    """
    Convert PDF to LaTeX using MathPix API
    
    ⚠️ NOT IMPLEMENTED YET - This endpoint is placeholder for future implementation
    
    Will require:
    - MATHPIX_APP_ID environment variable
    - MATHPIX_APP_KEY environment variable
    """
    raise HTTPException(
        status_code=501,
        detail="MathPix PDF to LaTeX conversion not implemented yet. Please upload LaTeX files directly."
    )
