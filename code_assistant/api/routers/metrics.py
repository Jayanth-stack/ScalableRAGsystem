"""Code metrics API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Dict
from datetime import datetime

from ..models import MetricsRequest, MetricsResponse
from ...analyzers.analyzer_factory import AnalyzerFactory
from ...parsers.parser_factory import ParserFactory

router = APIRouter()

@router.post("/", response_model=MetricsResponse)
async def calculate_metrics(request: MetricsRequest):
    """Calculate code quality metrics."""
    try:
        target_path = Path(request.target)
        
        if not target_path.exists():
            raise ValueError(f"Target path {target_path} does not exist")
        
        metrics = {}
        file_count = 0
        total_lines = 0
        
        # Handle single file vs directory
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*.py"))  # Extend for other languages
        
        file_count = len(files)
        
        # Process each file
        for file_path in files:
            parser = ParserFactory.create_parser_from_file(file_path)
            if not parser:
                continue
                
            result = parser.parse_file(file_path)
            if not result.success:
                continue
                
            total_lines += result.file_info.lines_count
            
            # Run requested metric analyzers
            for metric_type in request.metric_types:
                if metric_type == "complexity":
                    analyzer = AnalyzerFactory.create_analyzer("complexity")
                    file_metrics = analyzer.analyze_file(file_path, result.code_elements)
                    metrics.setdefault("complexity", []).append(file_metrics)
                elif metric_type == "quality":
                    # Calculate quality score
                    quality_score = calculate_quality_score(result)
                    metrics.setdefault("quality", []).append(quality_score)
        
        # Aggregate metrics
        aggregated = aggregate_metrics(metrics)
        
        return MetricsResponse(
            metrics=aggregated,
            timestamp=datetime.now(),
            file_count=file_count,
            total_lines=total_lines
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_quality_score(result) -> Dict:
    """Calculate quality score for parsed code."""
    elements = result.code_elements
    
    # Simple quality metrics
    functions_with_docs = sum(1 for e in elements if e.element_type == "function" and e.docstring)
    total_functions = sum(1 for e in elements if e.element_type == "function")
    
    doc_coverage = functions_with_docs / total_functions if total_functions > 0 else 0
    
    return {
        "documentation_coverage": doc_coverage,
        "total_elements": len(elements),
        "functions": total_functions,
        "classes": sum(1 for e in elements if e.element_type == "class")
    }

def aggregate_metrics(metrics: Dict) -> Dict:
    """Aggregate metrics across multiple files."""
    aggregated = {}
    
    for metric_type, values in metrics.items():
        if metric_type == "complexity":
            # Average complexity metrics
            if values:
                total_cc = sum(v.get("complexity", {}).get("cyclomatic", 0) for v in values)
                avg_mi = sum(v.get("complexity", {}).get("maintainability", 0) for v in values) / len(values)
                aggregated["complexity"] = {
                    "total_cyclomatic": total_cc,
                    "average_maintainability": avg_mi
                }
        elif metric_type == "quality":
            # Average quality metrics
            if values:
                avg_doc_coverage = sum(v.get("documentation_coverage", 0) for v in values) / len(values)
                total_elements = sum(v.get("total_elements", 0) for v in values)
                aggregated["quality"] = {
                    "average_documentation_coverage": avg_doc_coverage,
                    "total_code_elements": total_elements
                }
    
    return aggregated 