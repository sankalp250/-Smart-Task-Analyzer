"""
Smart Task Analyzer - Priority Scoring Algorithm

This module implements intelligent task prioritization based on multiple factors:
- Urgency (due date proximity)
- Importance (user-defined rating)
- Effort (estimated hours)
- Dependencies (blocking other tasks)
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from schemas import TaskBase, TaskResponse


class TaskScorer:
    """
    Calculates priority scores for tasks using configurable strategies.
    """
    
    # US Federal Holidays for 2025 (can be extended)
    HOLIDAYS_2025 = [
        "2025-01-01",  # New Year's Day
        "2025-01-20",  # Martin Luther King Jr. Day
        "2025-02-17",  # Presidents' Day
        "2025-05-26",  # Memorial Day
        "2025-07-04",  # Independence Day
        "2025-09-01",  # Labor Day
        "2025-10-13",  # Columbus Day
        "2025-11-11",  # Veterans Day
        "2025-11-27",  # Thanksgiving
        "2025-12-25",  # Christmas
    ]
    
    def __init__(self, strategy: str = "smart_balance", use_business_days: bool = True):
        self.strategy = strategy
        self.use_business_days = use_business_days
    
    def is_weekend(self, date: datetime) -> bool:
        """Check if a date falls on a weekend (Saturday=5, Sunday=6)."""
        return date.weekday() >= 5
    
    def is_holiday(self, date: datetime) -> bool:
        """Check if a date is a US federal holiday."""
        date_str = date.date().isoformat()
        return date_str in self.HOLIDAYS_2025
    
    def calculate_business_days(self, start_date: datetime, end_date: datetime) -> int:
        """
        Calculate number of business days between two dates.
        Excludes weekends and optionally holidays.
        """
        if start_date > end_date:
            return -self.calculate_business_days(end_date, start_date)
        
        business_days = 0
        current_date = start_date
        
        while current_date < end_date:
            if not self.is_weekend(current_date) and not self.is_holiday(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
        
    def detect_circular_dependencies(self, tasks: List[TaskBase]) -> List[int]:
        """
        Detect circular dependencies using DFS.
        Returns list of task indices involved in circular dependencies.
        """
        task_map = {i: task for i, task in enumerate(tasks)}
        visited = set()
        rec_stack = set()
        circular_tasks = set()
        
        def dfs(task_idx: int, path: set) -> bool:
            if task_idx in rec_stack:
                circular_tasks.update(path)
                return True
            if task_idx in visited:
                return False
                
            visited.add(task_idx)
            rec_stack.add(task_idx)
            path.add(task_idx)
            
            task = task_map.get(task_idx)
            if task and task.dependencies:
                for dep_id in task.dependencies:
                    if dep_id < len(tasks):
                        if dfs(dep_id, path.copy()):
                            circular_tasks.add(task_idx)
            
            rec_stack.remove(task_idx)
            return False
        
        for i in range(len(tasks)):
            if i not in visited:
                dfs(i, set())
        
        return list(circular_tasks)
    
    def calculate_urgency_score(self, due_date_str: str) -> float:
        """
        Calculate urgency score based on due date.
        Returns score between 0-200.
        
        With business days enabled:
        - Considers only weekdays (Mon-Fri)
        - Excludes federal holidays
        - Weekend due dates get urgency boost
        
        Scoring:
        - Past due: 100+ (with penalty multiplier)
        - Due today: 95
        - Due in 1-3 days: 80-90
        - Due in 4-7 days: 60-75
        - Due in 1-2 weeks: 40-55
        - Due in 2+ weeks: 10-35
        """
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate days until due
            if self.use_business_days:
                days_until_due = self.calculate_business_days(now, due_date)
                
                # Weekend boost: if due on weekend, increase urgency
                weekend_boost = 0
                if self.is_weekend(due_date):
                    weekend_boost = 10  # Extra urgency for weekend deadlines
            else:
                days_until_due = (due_date - now).days
                weekend_boost = 0
            
            # Base urgency calculation
            if days_until_due < 0:
                # Past due - exponential penalty
                overdue_days = abs(days_until_due)
                return min(100 + (overdue_days * 10), 200)
            elif days_until_due == 0:
                return 95 + weekend_boost
            elif days_until_due <= 1:
                return 90 + weekend_boost
            elif days_until_due <= 3:
                return 80 + weekend_boost
            elif days_until_due <= 7:
                return (70 - (days_until_due - 3) * 2.5) + weekend_boost
            elif days_until_due <= 14:
                return (55 - (days_until_due - 7) * 2) + weekend_boost
            elif days_until_due <= 30:
                return (35 - (days_until_due - 14) * 1.5) + weekend_boost
            else:
                return max(10, (35 - (days_until_due - 30) * 0.5) + weekend_boost)
        except (ValueError, AttributeError):
            # Invalid date format - return neutral score
            return 50
    
    def calculate_effort_score(self, estimated_hours: float, strategy: str) -> float:
        """
        Calculate effort score based on estimated hours.
        Strategy affects whether low or high effort is preferred.
        """
        if strategy == "fastest_wins":
            # Prefer quick tasks
            if estimated_hours <= 1:
                return 90
            elif estimated_hours <= 3:
                return 70
            elif estimated_hours <= 8:
                return 50
            else:
                return 30
        else:
            # Balanced approach - moderate effort is good
            if estimated_hours <= 2:
                return 70  # Quick wins
            elif estimated_hours <= 5:
                return 80  # Sweet spot
            elif estimated_hours <= 10:
                return 60
            else:
                return 40  # Large tasks
    
    def calculate_dependency_score(self, task_idx: int, tasks: List[TaskBase]) -> float:
        """
        Calculate how many tasks depend on this task.
        Tasks that block others get higher scores.
        """
        blocking_count = 0
        for i, task in enumerate(tasks):
            if task_idx in task.dependencies:
                blocking_count += 1
        
        # Each blocked task adds to the score
        return min(blocking_count * 20, 100)
    
    def calculate_priority_score(
        self, 
        task: TaskBase, 
        task_idx: int,
        all_tasks: List[TaskBase],
        circular_deps: List[int]
    ) -> Tuple[float, str]:
        """
        Calculate overall priority score and explanation.
        Returns (score, explanation)
        """
        # Check for circular dependency
        if task_idx in circular_deps:
            return (0, "⚠️ Circular dependency detected - needs resolution")
        
        # Validate data
        if not task.title or task.estimated_hours <= 0:
            return (0, "❌ Invalid task data")
        
        # Calculate component scores
        urgency = self.calculate_urgency_score(task.due_date)
        importance = task.importance * 10  # Scale 1-10 to 10-100
        effort = self.calculate_effort_score(task.estimated_hours, self.strategy)
        dependency = self.calculate_dependency_score(task_idx, all_tasks)
        
        # Apply strategy-specific weights
        if self.strategy == "fastest_wins":
            weights = {"urgency": 0.2, "importance": 0.2, "effort": 0.5, "dependency": 0.1}
        elif self.strategy == "high_impact":
            weights = {"urgency": 0.15, "importance": 0.6, "effort": 0.1, "dependency": 0.15}
        elif self.strategy == "deadline_driven":
            weights = {"urgency": 0.7, "importance": 0.15, "effort": 0.05, "dependency": 0.1}
        else:  # smart_balance
            weights = {"urgency": 0.35, "importance": 0.30, "effort": 0.20, "dependency": 0.15}
        
        # Calculate weighted score
        score = (
            urgency * weights["urgency"] +
            importance * weights["importance"] +
            effort * weights["effort"] +
            dependency * weights["dependency"]
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            urgency, importance, effort, dependency, task
        )
        
        return (round(score, 2), explanation)
    
    def _generate_explanation(
        self, 
        urgency: float, 
        importance: float, 
        effort: float, 
        dependency: float,
        task: TaskBase
    ) -> str:
        """Generate human-readable explanation for the score."""
        reasons = []
        
        # Urgency reasoning
        try:
            due_date = datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
            now = datetime.now()
            
            if self.use_business_days:
                days_until = self.calculate_business_days(now, due_date)
                day_type = "business days"
            else:
                days_until = (due_date - now).days
                day_type = "days"
            
            # Weekend indicator
            weekend_indicator = " 📅" if self.is_weekend(due_date) else ""
            
            if days_until < 0:
                reasons.append(f"🔴 OVERDUE by {abs(days_until)} {day_type}{weekend_indicator}")
            elif days_until == 0:
                reasons.append(f"🔴 Due TODAY{weekend_indicator}")
            elif days_until <= 3:
                reasons.append(f"🟡 Due in {days_until} {day_type}{weekend_indicator}")
            elif days_until <= 7:
                reasons.append(f"🟢 Due this week{weekend_indicator}")
        except:
            reasons.append("⚠️ Invalid due date")
        
        # Importance reasoning
        if task.importance >= 8:
            reasons.append(f"⭐ High importance ({task.importance}/10)")
        elif task.importance >= 5:
            reasons.append(f"Medium importance ({task.importance}/10)")
        
        # Effort reasoning
        if task.estimated_hours <= 2:
            reasons.append(f"⚡ Quick task ({task.estimated_hours}h)")
        elif task.estimated_hours >= 10:
            reasons.append(f"📊 Large task ({task.estimated_hours}h)")
        
        # Dependency reasoning
        if dependency > 0:
            reasons.append(f"🔗 Blocks other tasks")
        
        return " | ".join(reasons) if reasons else "Standard priority"
    
    def score_tasks(self, tasks: List[TaskBase]) -> List[TaskResponse]:
        """
        Score all tasks and return sorted list with scores and explanations.
        """
        # Detect circular dependencies
        circular_deps = self.detect_circular_dependencies(tasks)
        
        # Score each task
        scored_tasks = []
        for idx, task in enumerate(tasks):
            score, explanation = self.calculate_priority_score(
                task, idx, tasks, circular_deps
            )
            
            task_response = TaskResponse(
                id=idx,
                title=task.title,
                due_date=task.due_date,
                estimated_hours=task.estimated_hours,
                importance=task.importance,
                dependencies=task.dependencies,
                priority_score=score,
                explanation=explanation
            )
            scored_tasks.append(task_response)
        
        # Sort by priority score (descending)
        scored_tasks.sort(key=lambda x: x.priority_score or 0, reverse=True)
        
        return scored_tasks
    
    def suggest_top_tasks(self, tasks: List[TaskBase], count: int = 3) -> List[TaskResponse]:
        """
        Suggest top N tasks to work on today.
        """
        scored_tasks = self.score_tasks(tasks)
        
        # Filter out invalid tasks and circular dependencies
        valid_tasks = [t for t in scored_tasks if t.priority_score and t.priority_score > 0]
        
        return valid_tasks[:count]
