"""
Smart Task Analyzer - FastAPI Application
Main application with API endpoints for task analysis and suggestions.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from schemas import (
    TaskBase, 
    TaskAnalyzeRequest, 
    TaskAnalyzeResponse, 
    SuggestResponse,
    TaskResponse
)
from scoring import TaskScorer
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Task Analyzer API",
    description="Intelligent task prioritization and analysis system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Smart Task Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/tasks/analyze/",
            "suggest": "/api/tasks/suggest/",
            "docs": "/docs"
        }
    }


@app.post("/api/tasks/analyze/", response_model=TaskAnalyzeResponse)
async def analyze_tasks(request: TaskAnalyzeRequest):
    """
    Analyze and prioritize a list of tasks.
    
    Accepts a list of tasks and returns them sorted by priority score.
    Supports different sorting strategies:
    - smart_balance: Balanced approach considering all factors
    - fastest_wins: Prioritize low-effort tasks
    - high_impact: Prioritize importance over everything
    - deadline_driven: Prioritize based on due date
    
    Args:
        request: TaskAnalyzeRequest containing tasks and optional strategy
        
    Returns:
        TaskAnalyzeResponse with sorted tasks and their priority scores
    """
    try:
        if not request.tasks:
            raise HTTPException(status_code=400, detail="No tasks provided")
        
        # Validate strategy
        valid_strategies = ["smart_balance", "fastest_wins", "high_impact", "deadline_driven"]
        strategy = request.strategy or "smart_balance"
        
        if strategy not in valid_strategies:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid strategy. Must be one of: {', '.join(valid_strategies)}"
            )
        
        # Create scorer with specified strategy
        scorer = TaskScorer(strategy=strategy)
        
        # Score and sort tasks
        scored_tasks = scorer.score_tasks(request.tasks)
        
        return TaskAnalyzeResponse(
            tasks=scored_tasks,
            strategy_used=strategy
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/tasks/suggest/", response_model=SuggestResponse)
async def suggest_tasks(tasks: List[TaskBase]):
    """
    Suggest top 3 tasks to work on today.
    
    Analyzes all provided tasks and returns the top 3 highest priority tasks
    with explanations for why each was chosen.
    
    Args:
        tasks: List of tasks to analyze
        
    Returns:
        SuggestResponse with top 3 suggested tasks and total count
    """
    try:
        if not tasks:
            raise HTTPException(status_code=400, detail="No tasks provided")
        
        # Use smart_balance strategy for suggestions
        scorer = TaskScorer(strategy="smart_balance")
        
        # Get top 3 suggestions
        suggested = scorer.suggest_top_tasks(tasks, count=3)
        
        return SuggestResponse(
            suggested_tasks=suggested,
            total_tasks_analyzed=len(tasks)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Smart Task Analyzer"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
