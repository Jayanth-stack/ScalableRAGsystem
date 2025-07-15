"""Background task handlers."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict

from .models import AnalysisRequest
from ..parsers.parser_factory import ParserFactory
from ..analyzers.analyzer_factory import AnalyzerFactory

async def run_analysis_task(
    task_id: str,
    request: AnalysisRequest,
    tasks: Dict[str, Dict]
):
    """Run analysis task in background."""
    try:
        # Update status
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["updated_at"] = datetime.now()
        
        # Simulate progress updates
        for progress in [10, 30, 50, 70, 90]:
            tasks[task_id]["progress"] = progress
            await asyncio.sleep(0.5)  # Simulate work
        
        # Run actual analysis
        target_path = Path(request.target)
        
        # Parse file
        parser = ParserFactory.create_parser_from_file(target_path)
        result = parser.parse_file(target_path)
        
        if not result.success:
            raise ValueError(f"Failed to parse: {result.error_message}")
        
        # Run analyzers
        analysis_results = {}
        for analysis_type in request.analysis_types:
            analyzer = AnalyzerFactory.create_analyzer(analysis_type)
            analysis_results[analysis_type] = analyzer.analyze_file(
                target_path,
                result.code_elements
            )
        
        # Update task with results
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = {
            "file_info": result.file_info.dict(),
            "elements_count": len(result.code_elements),
            "analysis": analysis_results
        }
        tasks[task_id]["updated_at"] = datetime.now()
        
    except Exception as e:
        # Update task with error
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["updated_at"] = datetime.now() 