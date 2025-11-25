"""
Feedback System for Learning-based Task Prioritization
Stores user feedback and adjusts strategy weights accordingly
"""

from typing import Dict, List, Optional
from datetime import datetime


class FeedbackStore:
    """
    In-memory storage for user feedback on task suggestions.
    In production, this would be persisted to a database.
    """
    
    def __init__(self):
        self.feedback_history: List[Dict] = []
        self.strategy_preferences: Dict[str, int] = {
            'smart_balance': 0,
            'fastest_wins': 0,
            'high_impact': 0,
            'deadline_driven': 0
        }
        self.weight_adjustments: Dict[str, float] = {
            'urgency': 0.0,
            'importance': 0.0,
            'effort': 0.0,
            'dependencies': 0.0
        }
    
    def add_feedback(self, task_title: str, was_helpful: bool, strategy_used: str):
        """Record user feedback on a suggested task."""
        feedback = {
            'task_title': task_title,
            'was_helpful': was_helpful,
            'strategy_used': strategy_used,
            'timestamp': datetime.now().isoformat()
        }
        self.feedback_history.append(feedback)
        
        # Update strategy preferences
        if was_helpful:
            self.strategy_preferences[strategy_used] += 1
        else:
            self.strategy_preferences[strategy_used] -= 1
        
        # Adjust weights based on feedback patterns
        self._adjust_weights(strategy_used, was_helpful)
    
    def _adjust_weights(self, strategy: str, was_helpful: bool):
        """
        Adjust factor weights based on feedback.
        Positive feedback increases weights for that strategy's focus.
        Negative feedback decreases them.
        """
        adjustment = 0.02 if was_helpful else -0.02
        
        # Strategy-specific weight adjustments
        if strategy == 'deadline_driven':
            self.weight_adjustments['urgency'] += adjustment
        elif strategy == 'high_impact':
            self.weight_adjustments['importance'] += adjustment
        elif strategy == 'fastest_wins':
            self.weight_adjustments['effort'] += adjustment
        else:  # smart_balance
            # Distribute adjustment across all factors
            for factor in self.weight_adjustments:
                self.weight_adjustments[factor] += adjustment / 4
        
        # Clamp adjustments to reasonable range (-0.2 to +0.2)
        for factor in self.weight_adjustments:
            self.weight_adjustments[factor] = max(-0.2, min(0.2, self.weight_adjustments[factor]))
    
    def get_personalized_weights(self, base_strategy: str) -> Dict[str, float]:
        """
        Get personalized weights for a strategy based on user feedback.
        Returns adjusted weights that can be used in the scoring algorithm.
        """
        # Base weights for each strategy
        base_weights = {
            'smart_balance': {'urgency': 0.35, 'importance': 0.30, 'effort': 0.20, 'dependencies': 0.15},
            'fastest_wins': {'urgency': 0.25, 'importance': 0.20, 'effort': 0.40, 'dependencies': 0.15},
            'high_impact': {'urgency': 0.20, 'importance': 0.50, 'effort': 0.15, 'dependencies': 0.15},
            'deadline_driven': {'urgency': 0.50, 'importance': 0.25, 'effort': 0.10, 'dependencies': 0.15}
        }
        
        weights = base_weights.get(base_strategy, base_weights['smart_balance']).copy()
        
        # Apply personalized adjustments
        for factor, adjustment in self.weight_adjustments.items():
            weights[factor] += adjustment
        
        # Normalize to ensure weights sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def get_recommended_strategy(self) -> str:
        """Get the strategy with the most positive feedback."""
        if not self.feedback_history:
            return 'smart_balance'
        
        # Find strategy with highest preference score
        best_strategy = max(self.strategy_preferences.items(), key=lambda x: x[1])
        
        # Only recommend if it has positive feedback
        if best_strategy[1] > 0:
            return best_strategy[0]
        
        return 'smart_balance'
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of feedback statistics."""
        total_feedback = len(self.feedback_history)
        if total_feedback == 0:
            return {
                'total_feedback': 0,
                'helpful_count': 0,
                'helpful_percentage': 0,
                'recommended_strategy': 'smart_balance',
                'weight_adjustments': self.weight_adjustments
            }
        
        helpful_count = sum(1 for f in self.feedback_history if f['was_helpful'])
        
        return {
            'total_feedback': total_feedback,
            'helpful_count': helpful_count,
            'helpful_percentage': round((helpful_count / total_feedback) * 100, 1),
            'recommended_strategy': self.get_recommended_strategy(),
            'weight_adjustments': self.weight_adjustments,
            'strategy_preferences': self.strategy_preferences
        }


# Global feedback store instance
feedback_store = FeedbackStore()
