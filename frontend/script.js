/**
 * Smart Task Analyzer - Frontend JavaScript
 * Handles API communication, form validation, and UI interactions
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let tasks = [];
let currentStrategy = 'smart_balance';

// DOM Elements
const elements = {
    // Strategy cards
    strategyCards: document.querySelectorAll('.strategy-card'),
    
    // Input mode toggle
    toggleBtns: document.querySelectorAll('.toggle-btn'),
    formMode: document.getElementById('form-mode'),
    jsonMode: document.getElementById('json-mode'),
    
    // Form elements
    taskForm: document.getElementById('task-form'),
    taskTitle: document.getElementById('task-title'),
    taskDueDate: document.getElementById('task-due-date'),
    taskHours: document.getElementById('task-hours'),
    taskImportance: document.getElementById('task-importance'),
    taskDependencies: document.getElementById('task-dependencies'),
    
    // Task list
    taskListContainer: document.getElementById('task-list-container'),
    taskList: document.getElementById('task-list'),
    taskCount: document.getElementById('task-count'),
    clearTasksBtn: document.getElementById('clear-tasks'),
    
    // JSON input
    jsonInput: document.getElementById('json-input'),
    loadJsonBtn: document.getElementById('load-json'),
    
    // Analyze button
    analyzeBtn: document.getElementById('analyze-btn'),
    
    // Results
    resultsSection: document.getElementById('results-section'),
    strategyUsed: document.getElementById('strategy-used'),
    resultsCount: document.getElementById('results-count'),
    suggestionsList: document.getElementById('suggestions-list'),
    resultsList: document.getElementById('results-list'),
    suggestionsContainer: document.getElementById('suggestions-container'),
    
    // Loading and error
    loadingOverlay: document.getElementById('loading-overlay'),
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    setDefaultDueDate();
});

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    // Strategy selection
    elements.strategyCards.forEach(card => {
        card.addEventListener('click', () => selectStrategy(card));
    });
    
    // Input mode toggle
    elements.toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => toggleInputMode(btn));
    });
    
    // Form submission
    elements.taskForm.addEventListener('submit', handleFormSubmit);
    
    // Clear tasks
    elements.clearTasksBtn.addEventListener('click', clearAllTasks);
    
    // Load JSON
    elements.loadJsonBtn.addEventListener('click', loadTasksFromJSON);
    
    // Analyze tasks
    elements.analyzeBtn.addEventListener('click', analyzeTasks);
}

/**
 * Set default due date to today
 */
function setDefaultDueDate() {
    const today = new Date().toISOString().split('T')[0];
    elements.taskDueDate.value = today;
}

/**
 * Select prioritization strategy
 */
function selectStrategy(selectedCard) {
    elements.strategyCards.forEach(card => card.classList.remove('active'));
    selectedCard.classList.add('active');
    currentStrategy = selectedCard.dataset.strategy;
}

/**
 * Toggle between form and JSON input modes
 */
function toggleInputMode(selectedBtn) {
    elements.toggleBtns.forEach(btn => btn.classList.remove('active'));
    selectedBtn.classList.add('active');
    
    const mode = selectedBtn.dataset.mode;
    if (mode === 'form') {
        elements.formMode.style.display = 'block';
        elements.jsonMode.style.display = 'none';
    } else {
        elements.formMode.style.display = 'none';
        elements.jsonMode.style.display = 'block';
    }
}

/**
 * Handle form submission
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Parse dependencies
    const depsInput = elements.taskDependencies.value.trim();
    const dependencies = depsInput 
        ? depsInput.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d))
        : [];
    
    // Create task object
    const task = {
        title: elements.taskTitle.value.trim(),
        due_date: elements.taskDueDate.value,
        estimated_hours: parseFloat(elements.taskHours.value),
        importance: parseInt(elements.taskImportance.value),
        dependencies: dependencies
    };
    
    // Validate task
    if (!validateTask(task)) {
        return;
    }
    
    // Add task to list
    tasks.push(task);
    updateTaskList();
    
    // Reset form
    elements.taskForm.reset();
    setDefaultDueDate();
    
    // Show success feedback
    showNotification('Task added successfully!', 'success');
}

/**
 * Validate task data
 */
function validateTask(task) {
    if (!task.title || task.title.length === 0) {
        showError('Task title is required');
        return false;
    }
    
    if (!task.due_date) {
        showError('Due date is required');
        return false;
    }
    
    if (task.estimated_hours <= 0) {
        showError('Estimated hours must be greater than 0');
        return false;
    }
    
    if (task.importance < 1 || task.importance > 10) {
        showError('Importance must be between 1 and 10');
        return false;
    }
    
    return true;
}

/**
 * Update task list display
 */
function updateTaskList() {
    if (tasks.length === 0) {
        elements.taskListContainer.style.display = 'none';
        elements.analyzeBtn.disabled = true;
        return;
    }
    
    elements.taskListContainer.style.display = 'block';
    elements.analyzeBtn.disabled = false;
    elements.taskCount.textContent = tasks.length;
    
    elements.taskList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div class="task-item-info">
                <div class="task-item-title">${escapeHtml(task.title)}</div>
                <div class="task-item-meta">
                    <span>📅 ${formatDate(task.due_date)}</span>
                    <span>⏱️ ${task.estimated_hours}h</span>
                    <span>⭐ ${task.importance}/10</span>
                    ${task.dependencies.length > 0 ? `<span>🔗 Deps: ${task.dependencies.join(', ')}</span>` : ''}
                </div>
            </div>
            <button class="task-item-remove" onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

/**
 * Remove task from list
 */
function removeTask(index) {
    tasks.splice(index, 1);
    updateTaskList();
    showNotification('Task removed', 'info');
}

/**
 * Clear all tasks
 */
function clearAllTasks() {
    if (tasks.length === 0) return;
    
    if (confirm('Are you sure you want to clear all tasks?')) {
        tasks = [];
        updateTaskList();
        elements.resultsSection.style.display = 'none';
        showNotification('All tasks cleared', 'info');
    }
}

/**
 * Load tasks from JSON input
 */
function loadTasksFromJSON() {
    const jsonText = elements.jsonInput.value.trim();
    
    if (!jsonText) {
        showError('Please enter JSON data');
        return;
    }
    
    try {
        const parsedTasks = JSON.parse(jsonText);
        
        if (!Array.isArray(parsedTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate all tasks
        for (const task of parsedTasks) {
            if (!validateTask(task)) {
                return;
            }
        }
        
        // Add tasks
        tasks = parsedTasks;
        updateTaskList();
        
        // Switch to form mode to show tasks
        document.querySelector('[data-mode="form"]').click();
        
        showNotification(`${tasks.length} tasks loaded from JSON`, 'success');
        
    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
}

/**
 * Analyze tasks using API
 */
async function analyzeTasks() {
    if (tasks.length === 0) {
        showError('Please add some tasks first');
        return;
    }
    
    // Show loading
    elements.loadingOverlay.style.display = 'flex';
    
    try {
        // Call analyze endpoint
        const analyzeResponse = await fetch(`${API_BASE_URL}/api/tasks/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: currentStrategy
            })
        });
        
        if (!analyzeResponse.ok) {
            const errorData = await analyzeResponse.json();
            throw new Error(errorData.detail || 'Failed to analyze tasks');
        }
        
        const analyzeData = await analyzeResponse.json();
        
        // Call suggest endpoint
        const suggestResponse = await fetch(`${API_BASE_URL}/api/tasks/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tasks)
        });
        
        if (!suggestResponse.ok) {
            const errorData = await suggestResponse.json();
            throw new Error(errorData.detail || 'Failed to get suggestions');
        }
        
        const suggestData = await suggestResponse.json();
        
        // Display results
        displayResults(analyzeData, suggestData);
        
        // Hide loading
        elements.loadingOverlay.style.display = 'none';
        
        // Scroll to results
        elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        elements.loadingOverlay.style.display = 'none';
        showError('Error analyzing tasks: ' + error.message);
    }
}

/**
 * Display analysis results
 */
function displayResults(analyzeData, suggestData) {
    // Show results section
    elements.resultsSection.style.display = 'block';
    
    // Update meta information
    const strategyNames = {
        'smart_balance': 'Smart Balance',
        'fastest_wins': 'Fastest Wins',
        'high_impact': 'High Impact',
        'deadline_driven': 'Deadline Driven'
    };
    
    elements.strategyUsed.textContent = `Strategy: ${strategyNames[analyzeData.strategy_used]}`;
    elements.resultsCount.textContent = `${analyzeData.tasks.length} tasks analyzed`;
    
    // Display suggestions
    if (suggestData.suggested_tasks.length > 0) {
        elements.suggestionsContainer.style.display = 'block';
        elements.suggestionsList.innerHTML = suggestData.suggested_tasks
            .map((task, index) => createResultCard(task, index + 1, true))
            .join('');
    } else {
        elements.suggestionsContainer.style.display = 'none';
    }
    
    // Display all tasks
    elements.resultsList.innerHTML = analyzeData.tasks
        .map((task, index) => createResultCard(task, index + 1, false))
        .join('');
}

/**
 * Create result card HTML
 */
function createResultCard(task, rank, isSuggestion) {
    const priorityClass = getPriorityClass(task.priority_score);
    const rankBadge = isSuggestion ? `<span style="font-size: 1.5rem; margin-right: 0.5rem;">${getRankEmoji(rank)}</span>` : '';
    
    return `
        <div class="result-card ${priorityClass}">
            <div class="result-header">
                <div class="result-title">
                    ${rankBadge}${escapeHtml(task.title)}
                </div>
                <div class="priority-score">
                    Score: ${task.priority_score.toFixed(1)}
                </div>
            </div>
            
            ${task.explanation ? `
                <div class="result-explanation">
                    ${escapeHtml(task.explanation)}
                </div>
            ` : ''}
            
            <div class="result-meta">
                <div class="meta-item">
                    <span>📅</span>
                    <span>Due: ${formatDate(task.due_date)}</span>
                </div>
                <div class="meta-item">
                    <span>⏱️</span>
                    <span>Effort: ${task.estimated_hours}h</span>
                </div>
                <div class="meta-item">
                    <span>⭐</span>
                    <span>Importance: ${task.importance}/10</span>
                </div>
                ${task.dependencies.length > 0 ? `
                    <div class="meta-item">
                        <span>🔗</span>
                        <span>Dependencies: ${task.dependencies.join(', ')}</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

/**
 * Get priority class based on score
 */
function getPriorityClass(score) {
    if (score >= 100) return 'priority-critical';
    if (score >= 70) return 'priority-high';
    if (score >= 40) return 'priority-medium';
    return 'priority-low';
}

/**
 * Get rank emoji
 */
function getRankEmoji(rank) {
    const emojis = ['🥇', '🥈', '🥉'];
    return emojis[rank - 1] || '📌';
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const taskDate = new Date(date);
    taskDate.setHours(0, 0, 0, 0);
    
    const diffTime = taskDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
        return `${Math.abs(diffDays)} days ago (OVERDUE)`;
    } else if (diffDays === 0) {
        return 'Today';
    } else if (diffDays === 1) {
        return 'Tomorrow';
    } else if (diffDays <= 7) {
        return `In ${diffDays} days`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.style.display = 'flex';
}

/**
 * Show notification (simple implementation)
 */
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4facfe' : '#667eea'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Make removeTask available globally
window.removeTask = removeTask;
