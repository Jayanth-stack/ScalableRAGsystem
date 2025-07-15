"""Analysis API endpoints."""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Dict
import uuid
from pathlib import Path
from datetime import datetime

from ..models import AnalysisRequest, AnalysisResponse, TaskStatusResponse
from ..tasks import run_analysis_task
from ...parsers.parser_factory import ParserFactory
from ...analyzers.analyzer_factory import AnalyzerFactory

router = APIRouter()

# In-memory task storage (use Redis in production)
tasks: Dict[str, Dict] = {}

@router.post("/", response_model=AnalysisResponse)
async def analyze_code(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze code files or repositories."""
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "status": "pending",
        "created_at": datetime.now(),
        "request": request
    }
    
    if request.async_mode:
        # Run in background
        background_tasks.add_task(
            run_analysis_task,
            task_id,
            request,
            tasks
        )
        return AnalysisResponse(
            task_id=task_id,
            status="pending",
            created_at=tasks[task_id]["created_at"]
        )
    else:
        # Run synchronously
        try:
            result = await run_analysis_sync(request)
            return AnalysisResponse(
                task_id=task_id,
                status="completed",
                created_at=tasks[task_id]["created_at"],
                result=result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_analysis_status(task_id: str):
    """Get status of an analysis task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress"),
        result=task.get("result"),
        error=task.get("error"),
        created_at=task["created_at"],
        updated_at=task.get("updated_at", task["created_at"])
    )

async def run_analysis_sync(request: AnalysisRequest) -> Dict:
    """Run analysis synchronously."""
    target_path = Path(request.target)
    
    if not target_path.exists():
        raise ValueError(f"Target path {target_path} does not exist")
    
    # Parse file
    parser = ParserFactory.create_parser_from_file(target_path)
    if not parser:
        raise ValueError(f"No parser available for {target_path}")
    
    result = parser.parse_file(target_path)
    if not result.success:
        raise ValueError(f"Failed to parse: {result.error_message}")
    
    # Run requested analyzers
    analysis_results = {}
    for analysis_type in request.analysis_types:
        try:
            analyzer = AnalyzerFactory.create_analyzer(analysis_type)
            analysis_results[analysis_type] = analyzer.analyze_file(
                target_path,
                result.code_elements
            )
        except Exception as e:
            analysis_results[analysis_type] = {"error": str(e)}
    
    return {
        "file_info": result.file_info.dict(),
        "elements_count": len(result.code_elements),
        "analysis": analysis_results
    } 