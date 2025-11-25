"""
Quick API test script to verify endpoints are working
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200

def test_analyze():
    """Test analyze endpoint"""
    print("Testing analyze endpoint...")
    
    # Create sample tasks
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    next_week = (datetime.now() + timedelta(days=7)).date().isoformat()
    overdue = (datetime.now() - timedelta(days=2)).date().isoformat()
    
    tasks = [
        {
            "title": "Fix critical bug",
            "due_date": today,
            "estimated_hours": 2.0,
            "importance": 9,
            "dependencies": []
        },
        {
            "title": "Write documentation",
            "due_date": next_week,
            "estimated_hours": 5.0,
            "importance": 5,
            "dependencies": []
        },
        {
            "title": "Overdue task",
            "due_date": overdue,
            "estimated_hours": 3.0,
            "importance": 7,
            "dependencies": []
        },
        {
            "title": "Quick win task",
            "due_date": tomorrow,
            "estimated_hours": 1.0,
            "importance": 6,
            "dependencies": []
        }
    ]
    
    payload = {
        "tasks": tasks,
        "strategy": "smart_balance"
    }
    
    response = requests.post(f"{API_BASE}/api/tasks/analyze/", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Strategy used: {data['strategy_used']}")
        print(f"Tasks analyzed: {len(data['tasks'])}")
        print("\nTop 3 tasks by priority:")
        for i, task in enumerate(data['tasks'][:3], 1):
            print(f"{i}. {task['title']}")
            print(f"   Score: {task['priority_score']}")
            print(f"   Explanation: {task['explanation']}\n")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_suggest():
    """Test suggest endpoint"""
    print("\nTesting suggest endpoint...")
    
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now() + timedelta(days=1)).date().isoformat()
    
    tasks = [
        {
            "title": "High priority task",
            "due_date": today,
            "estimated_hours": 2.0,
            "importance": 9,
            "dependencies": []
        },
        {
            "title": "Medium priority task",
            "due_date": tomorrow,
            "estimated_hours": 3.0,
            "importance": 6,
            "dependencies": []
        }
    ]
    
    response = requests.post(f"{API_BASE}/api/tasks/suggest/", json=tasks)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total tasks analyzed: {data['total_tasks_analyzed']}")
        print(f"Suggestions: {len(data['suggested_tasks'])}")
        print("\nSuggested tasks:")
        for i, task in enumerate(data['suggested_tasks'], 1):
            print(f"{i}. {task['title']} (Score: {task['priority_score']})")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("Smart Task Analyzer - API Test")
    print("=" * 60 + "\n")
    
    try:
        health_ok = test_health()
        analyze_ok = test_analyze()
        suggest_ok = test_suggest()
        
        print("\n" + "=" * 60)
        print("Test Results:")
        print(f"Health Check: {'✓ PASS' if health_ok else '✗ FAIL'}")
        print(f"Analyze Endpoint: {'✓ PASS' if analyze_ok else '✗ FAIL'}")
        print(f"Suggest Endpoint: {'✓ PASS' if suggest_ok else '✗ FAIL'}")
        print("=" * 60)
        
        if all([health_ok, analyze_ok, suggest_ok]):
            print("\n✓ All tests passed!")
        else:
            print("\n✗ Some tests failed")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API server")
        print("Make sure the backend server is running on http://localhost:8000")
