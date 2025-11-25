# Smart Task Analyzer

> An intelligent task management system that prioritizes tasks based on multiple factors using advanced algorithms.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Algorithm Explanation](#algorithm-explanation)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Design Decisions](#design-decisions)
- [Time Breakdown](#time-breakdown)
- [Testing](#testing)
- [Future Improvements](#future-improvements)

## 🎯 Overview

Smart Task Analyzer is a mini-application built for a technical assessment that demonstrates problem-solving ability, algorithmic thinking, and clean code practices. The system intelligently scores and prioritizes tasks based on urgency, importance, effort, and dependencies.

**Tech Stack:**
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Testing:** Pytest

## ✨ Features

### Core Features
- ✅ **Intelligent Priority Scoring** - Multi-factor algorithm considering urgency, importance, effort, and dependencies
- ✅ **Multiple Sorting Strategies** - Smart Balance, Fastest Wins, High Impact, Deadline Driven
- ✅ **Circular Dependency Detection** - Automatically detects and flags circular dependencies
- ✅ **Dual Input Modes** - Form-based input or bulk JSON import
- ✅ **Real-time Validation** - Client and server-side validation
- ✅ **Top 3 Suggestions** - AI-powered recommendations for what to work on today
- ✅ **Professional UI** - Modern dark theme with animations and responsive design

### Edge Case Handling
- ✅ Past-due tasks with exponential penalty
- ✅ Missing or invalid data validation
- ✅ Circular dependency detection using DFS
- ✅ Configurable algorithm weights per strategy

## 🧠 Algorithm Explanation

### Priority Scoring Formula

The priority score is calculated using a weighted combination of four factors:

```
Priority Score = (Urgency × W₁) + (Importance × W₂) + (Effort × W₃) + (Dependencies × W₄)
```

### Factor Breakdown

#### 1. **Urgency Score (0-200)**
Based on due date proximity with special handling for overdue tasks:

- **Overdue:** 100+ with exponential penalty (10 points per day overdue)
- **Due Today:** 95 points
- **Due in 1-3 days:** 80-90 points
- **Due in 4-7 days:** 60-75 points
- **Due in 1-2 weeks:** 40-55 points
- **Due in 2+ weeks:** 10-35 points

**Rationale:** Overdue tasks receive scores above 100 to ensure they're prioritized. The exponential penalty ensures severely overdue tasks rise to the top.

#### 2. **Importance Score (10-100)**
User-provided rating scaled from 1-10 to 10-100.

**Rationale:** Direct user input on task importance. Scaled to match the 0-100 range of other factors.

#### 3. **Effort Score (30-90)**
Varies by strategy:

**Smart Balance / High Impact / Deadline Driven:**
- 1-2 hours: 70 points (quick wins)
- 2-5 hours: 80 points (sweet spot)
- 5-10 hours: 60 points
- 10+ hours: 40 points

**Fastest Wins:**
- ≤1 hour: 90 points
- 1-3 hours: 70 points
- 3-8 hours: 50 points
- 8+ hours: 30 points

**Rationale:** Moderate-effort tasks often provide the best ROI. The "Fastest Wins" strategy inverts this to prioritize quick completions.

#### 4. **Dependency Score (0-100)**
Each task that depends on this task adds 20 points (capped at 100).

**Rationale:** Tasks that block other tasks should be completed first to unblock the dependency chain.

### Strategy Weights

Different strategies apply different weights to each factor:

| Strategy | Urgency | Importance | Effort | Dependencies |
|----------|---------|------------|--------|--------------|
| **Smart Balance** | 35% | 30% | 20% | 15% |
| **Fastest Wins** | 20% | 20% | 50% | 10% |
| **High Impact** | 15% | 60% | 10% | 15% |
| **Deadline Driven** | 70% | 15% | 5% | 10% |

### Circular Dependency Detection

Uses Depth-First Search (DFS) with a recursion stack to detect cycles:

1. Maintain a visited set and recursion stack
2. For each unvisited task, perform DFS
3. If a task in the recursion stack is encountered again, a cycle exists
4. Tasks involved in cycles receive a score of 0 and a warning

**Rationale:** Circular dependencies are impossible to resolve without breaking the cycle, so they must be flagged for manual intervention.

### Example Calculation

**Task:** "Fix critical bug"
- Due: Today
- Importance: 9/10
- Effort: 2 hours
- Blocks: 2 other tasks

**Using Smart Balance Strategy:**
```
Urgency: 95 × 0.35 = 33.25
Importance: 90 × 0.30 = 27.00
Effort: 70 × 0.20 = 14.00
Dependencies: 40 × 0.15 = 6.00
─────────────────────────────
Total Score: 80.25
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sankalp250/-Smart-Task-Analyzer.git
cd Smart-Task-Analyzer
```

2. **Create and activate virtual environment**

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Run the backend server**
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

5. **Open the frontend**

Open `frontend/index.html` in your web browser, or use a simple HTTP server:

```bash
# Python 3
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

### Running Tests

```bash
cd backend
pytest test_scoring.py -v
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Analyze Tasks
```http
POST /api/tasks/analyze/
```

**Request Body:**
```json
{
  "tasks": [
    {
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "id": 0,
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": [],
      "priority_score": 75.5,
      "explanation": "🟢 Due in 5 days | ⭐ High importance (8/10)"
    }
  ],
  "strategy_used": "smart_balance"
}
```

#### 2. Get Suggestions
```http
POST /api/tasks/suggest/
```

**Request Body:**
```json
[
  {
    "title": "Fix login bug",
    "due_date": "2025-11-30",
    "estimated_hours": 3,
    "importance": 8,
    "dependencies": []
  }
]
```

**Response:**
```json
{
  "suggested_tasks": [...],
  "total_tasks_analyzed": 5
}
```

#### 3. Health Check
```http
GET /api/health
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎨 Design Decisions

### 1. **FastAPI over Django**
**Decision:** Used FastAPI instead of the suggested Django.

**Rationale:**
- Faster development for API-only applications
- Automatic API documentation
- Better performance for async operations
- Modern Python features (type hints, async/await)
- Lighter weight for this use case

### 2. **Weighted Scoring vs. Rule-Based**
**Decision:** Implemented configurable weighted scoring rather than hard rules.

**Rationale:**
- More flexible and adaptable to different user preferences
- Allows for strategy customization
- Easier to tune and optimize
- Provides smooth transitions rather than hard cutoffs

### 3. **Client-Side + Server-Side Validation**
**Decision:** Implemented validation on both frontend and backend.

**Rationale:**
- Client-side: Better UX with immediate feedback
- Server-side: Security and data integrity
- Defense in depth approach

### 4. **Exponential Penalty for Overdue Tasks**
**Decision:** Overdue tasks get 100+ score with 10 points per day penalty.

**Rationale:**
- Ensures overdue tasks always rank high
- Severity increases with time overdue
- Prevents old overdue tasks from being ignored

### 5. **DFS for Circular Dependency Detection**
**Decision:** Used Depth-First Search with recursion stack.

**Rationale:**
- O(V + E) time complexity - efficient
- Standard graph algorithm for cycle detection
- Easy to understand and maintain
- Correctly identifies all tasks in cycles

### 6. **Modern Dark Theme UI**
**Decision:** Implemented dark theme with gradients and animations.

**Rationale:**
- Reduces eye strain for extended use
- Modern, professional appearance
- Gradients and animations enhance UX
- Responsive design for all devices

### Trade-offs

1. **SQLite vs. PostgreSQL:** Chose SQLite for simplicity and portability. Trade-off: Less suitable for production with concurrent users.

2. **Vanilla JS vs. React:** Chose vanilla JavaScript for simplicity and no build step. Trade-off: More verbose code, less maintainable for very large applications.

3. **Fixed Weights vs. ML:** Used fixed strategy weights rather than machine learning. Trade-off: Less adaptive but more predictable and explainable.

## ⏱️ Time Breakdown

| Task | Estimated | Actual |
|------|-----------|--------|
| **Backend Development** | 2h | 2.5h |
| - Database models & schemas | 20min | 25min |
| - Scoring algorithm | 60min | 75min |
| - API endpoints | 30min | 35min |
| - Unit tests | 10min | 15min |
| **Frontend Development** | 1.5h | 2h |
| - HTML structure | 20min | 25min |
| - CSS styling | 40min | 50min |
| - JavaScript logic | 30min | 45min |
| **Documentation** | 30min | 45min |
| - README | 20min | 30min |
| - Code comments | 10min | 15min |
| **Testing & Debugging** | 30min | 45min |
| **Total** | **4.5h** | **5.75h** |

## 🧪 Testing

### Unit Tests

The project includes comprehensive unit tests for the scoring algorithm:

```bash
cd backend
pytest test_scoring.py -v
```

**Test Coverage:**
- ✅ Urgency calculation for various date ranges
- ✅ Effort scoring across different strategies
- ✅ Circular dependency detection
- ✅ Dependency scoring
- ✅ Task sorting and prioritization
- ✅ Invalid data handling
- ✅ Strategy comparison

### Manual Testing Checklist

- [x] Add tasks via form
- [x] Add tasks via JSON
- [x] Switch between strategies
- [x] Analyze tasks
- [x] View suggestions
- [x] Remove individual tasks
- [x] Clear all tasks
- [x] Test with overdue tasks
- [x] Test with circular dependencies
- [x] Test responsive design
- [x] Test error handling

## 🚀 Future Improvements

Given more time, I would implement:

### High Priority
1. **Persistent Storage** - Save tasks to database instead of in-memory
2. **User Authentication** - Multi-user support with personal task lists
3. **Task Editing** - Ability to edit existing tasks
4. **Dependency Graph Visualization** - Visual representation of task dependencies using D3.js or similar

### Medium Priority
5. **Date Intelligence** - Consider weekends/holidays in urgency calculation
6. **Eisenhower Matrix View** - 2D visualization of urgent vs. important
7. **Task History** - Track completed tasks and time taken
8. **Export Functionality** - Export tasks and analysis to PDF/CSV

### Low Priority
9. **Learning System** - Adjust algorithm based on user feedback
10. **Recurring Tasks** - Support for repeating tasks
11. **Tags & Categories** - Organize tasks by project or category
12. **Mobile App** - Native mobile application
13. **Notifications** - Email/push notifications for upcoming deadlines
14. **Team Collaboration** - Share tasks and collaborate with team members

### Technical Improvements
- **Caching** - Redis caching for frequently accessed data
- **Rate Limiting** - API rate limiting for production
- **Logging** - Comprehensive logging system
- **CI/CD Pipeline** - Automated testing and deployment
- **Docker** - Containerization for easy deployment
- **Performance Optimization** - Database indexing, query optimization

## 📝 License

This project was created as part of a technical assessment.

## 👤 Author

**Sankalp**
- GitHub: [@sankalp250](https://github.com/sankalp250)

---

**Note:** This project was completed as part of a Software Development Intern technical assessment, focusing on problem-solving, algorithm design, and clean code practices.
