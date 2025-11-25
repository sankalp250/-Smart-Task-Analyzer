from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    due_date: str
    estimated_hours: float = Field(..., gt=0)
    importance: int = Field(..., ge=1, le=10)
    dependencies: List[int] = Field(default_factory=list)

    @validator('due_date')
    def validate_due_date(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid date format. Use ISO format (YYYY-MM-DD)')

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    priority_score: Optional[float] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class TaskAnalyzeRequest(BaseModel):
    tasks: List[TaskBase]
    strategy: Optional[str] = "smart_balance"

class TaskAnalyzeResponse(BaseModel):
    tasks: List[TaskResponse]
    strategy_used: str

class SuggestResponse(BaseModel):
    suggested_tasks: List[TaskResponse]
    total_tasks_analyzed: int
