"""Documentation generation API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List

from ..models import DocumentationRequest, DocumentationResponse
from ...core.config import Settings
from google.generativeai import GenerativeModel

router = APIRouter()
settings = Settings()

# Initialize Gemini model
model = GenerativeModel('gemini-1.5-pro')

@router.post("/", response_model=DocumentationResponse)
async def generate_documentation(request: DocumentationRequest):
    """Generate documentation for code elements."""
    try:
        # Read target code
        target_path = Path(request.target)
        if target_path.exists():
            with open(target_path, 'r') as f:
                code_content = f.read()
        else:
            code_content = request.target  # Assume it's code snippet
        
        # Create prompt based on doc type and style
        prompt = create_documentation_prompt(
            code_content,
            request.doc_type,
            request.style,
            request.include_examples
        )
        
        # Generate documentation
        response = model.generate_content(prompt)
        
        return DocumentationResponse(
            documentation=response.text,
            confidence_score=0.95,  # Placeholder
            suggestions=[
                "Add more examples",
                "Include edge cases",
                "Document error handling"
            ]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_documentation_prompt(
    code: str,
    doc_type: str,
    style: str,
    include_examples: bool
) -> str:
    """Create prompt for documentation generation."""
    base_prompt = f"""
    Generate {style} style documentation for the following {doc_type}:
    
    ```python
    {code}
    ```
    
    Requirements:
    - Use {style} documentation format
    - Include clear descriptions
    - Document all parameters and return values
    """
    
    if include_examples:
        base_prompt += "\n- Include usage examples"
    
    return base_prompt

@router.post("/batch")
async def generate_batch_documentation(file_paths: List[str]):
    """Generate documentation for multiple files."""
    results = {}
    
    for file_path in file_paths:
        try:
            request = DocumentationRequest(target=file_path)
            response = await generate_documentation(request)
            results[file_path] = response.dict()
        except Exception as e:
            results[file_path] = {"error": str(e)}
    
    return results 