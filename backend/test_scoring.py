"""
Unit Tests for Smart Task Analyzer Scoring Algorithm
"""

import pytest
from datetime import datetime, timedelta
from schemas import TaskBase
from scoring import TaskScorer


class TestTaskScorer:
    """Test suite for TaskScorer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = TaskScorer(strategy="smart_balance")
        
        # Sample tasks for testing
        today = datetime.now().date().isoformat()
        tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
        next_week = (datetime.now() + timedelta(days=7)).date().isoformat()
        overdue = (datetime.now() - timedelta(days=2)).date().isoformat()
        
        self.sample_tasks = [
            TaskBase(
                title="Fix critical bug",
                due_date=today,
                estimated_hours=2.0,
                importance=9,
                dependencies=[]
            ),
            TaskBase(
                title="Write documentation",
                due_date=next_week,
                estimated_hours=5.0,
                importance=5,
                dependencies=[]
            ),
            TaskBase(
                title="Overdue task",
                due_date=overdue,
                estimated_hours=3.0,
                importance=7,
                dependencies=[]
            ),
        ]
    
    def test_urgency_score_overdue(self):
        """Test urgency score for overdue tasks."""
        overdue_date = (datetime.now() - timedelta(days=2)).date().isoformat()
        score = self.scorer.calculate_urgency_score(overdue_date)
        assert score > 100, "Overdue tasks should have score > 100"
    
    def test_urgency_score_today(self):
        """Test urgency score for tasks due today."""
        today = datetime.now().date().isoformat()
        score = self.scorer.calculate_urgency_score(today)
        assert score >= 90, "Tasks due today should have high urgency"
    
    def test_urgency_score_future(self):
        """Test urgency score for future tasks."""
        future = (datetime.now() + timedelta(days=30)).date().isoformat()
        score = self.scorer.calculate_urgency_score(future)
        assert score < 50, "Far future tasks should have lower urgency"
    
    def test_effort_score_fastest_wins(self):
        """Test effort scoring with fastest_wins strategy."""
        scorer = TaskScorer(strategy="fastest_wins")
        quick_task_score = scorer.calculate_effort_score(1.0, "fastest_wins")
        long_task_score = scorer.calculate_effort_score(10.0, "fastest_wins")
        assert quick_task_score > long_task_score, "Quick tasks should score higher in fastest_wins"
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        # Create tasks with circular dependency: 0 -> 1 -> 2 -> 0
        circular_tasks = [
            TaskBase(
                title="Task A",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[2]  # Depends on task 2
            ),
            TaskBase(
                title="Task B",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[0]  # Depends on task 0
            ),
            TaskBase(
                title="Task C",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[1]  # Depends on task 1
            ),
        ]
        
        circular_deps = self.scorer.detect_circular_dependencies(circular_tasks)
        assert len(circular_deps) > 0, "Should detect circular dependencies"
    
    def test_dependency_score(self):
        """Test dependency scoring - tasks that block others score higher."""
        tasks = [
            TaskBase(
                title="Blocking task",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[]
            ),
            TaskBase(
                title="Dependent task 1",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[0]
            ),
            TaskBase(
                title="Dependent task 2",
                due_date=datetime.now().date().isoformat(),
                estimated_hours=2.0,
                importance=5,
                dependencies=[0]
            ),
        ]
        
        score = self.scorer.calculate_dependency_score(0, tasks)
        assert score > 0, "Task blocking others should have positive dependency score"
    
    def test_score_tasks_sorting(self):
        """Test that tasks are properly sorted by priority."""
        scored = self.scorer.score_tasks(self.sample_tasks)
        
        # Check that we got all tasks back
        assert len(scored) == len(self.sample_tasks)
        
        # Check that scores are in descending order
        scores = [task.priority_score for task in scored if task.priority_score]
        assert scores == sorted(scores, reverse=True), "Tasks should be sorted by score descending"
    
    def test_invalid_date_handling(self):
        """Test handling of invalid date formats."""
        # Test the urgency calculator directly with invalid date
        # (bypassing Pydantic validation which would reject it)
        score = self.scorer.calculate_urgency_score("invalid-date")
        assert score == 50, "Invalid dates should return neutral score"
    
    def test_suggest_top_tasks(self):
        """Test suggesting top tasks."""
        suggestions = self.scorer.suggest_top_tasks(self.sample_tasks, count=2)
        
        assert len(suggestions) <= 2, "Should return at most requested count"
        assert all(task.priority_score and task.priority_score > 0 for task in suggestions), \
            "All suggestions should have valid scores"
    
    def test_different_strategies(self):
        """Test that different strategies produce different results."""
        strategies = ["smart_balance", "fastest_wins", "high_impact", "deadline_driven"]
        results = {}
        
        for strategy in strategies:
            scorer = TaskScorer(strategy=strategy)
            scored = scorer.score_tasks(self.sample_tasks)
            results[strategy] = [task.priority_score for task in scored]
        
        # At least some strategies should produce different orderings
        unique_results = len(set(tuple(r) for r in results.values()))
        assert unique_results > 1, "Different strategies should produce different results"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
