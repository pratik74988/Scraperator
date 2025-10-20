// ============================================
// AI Chat Interface JavaScript
// ============================================

let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
    setupEventListeners();
    autoResizeTextarea();
});

// Setup Event Listeners
function setupEventListeners() {
    const messageInput = document.getElementById('chatMessage');
    const urlInput = document.getElementById('chatUrl');
    
    // Send on Enter (Shift+Enter for new line)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
}

// Auto-resize textarea
function autoResizeTextarea() {
    const textarea = document.getElementById('chatMessage');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// Send Message
async function sendMessage() {
    const urlInput = document.getElementById('chatUrl');
    const messageInput = document.getElementById('chatMessage');
    const sendBtn = document.getElementById('sendBtn');
    
    const url = urlInput.value.trim();
    const message = messageInput.value.trim();
    
    if (!url || !message) {
        showNotification('Please enter both URL and message', 'warning');
        return;
    }
    
    // Validate URL
    if (!isValidUrl(url)) {
        showNotification('Please enter a valid URL', 'error');
        return;
    }
    
    // Disable input
    sendBtn.disabled = true;
    messageInput.disabled = true;
    urlInput.disabled = true;
    
    // Add user message to chat
    addUserMessage(message, url);
    
    // Clear input
    messageInput.value = '';
    autoResizeTextarea();
    
    // Show loading
    const loadingId = addLoadingMessage();
    
    // Determine request type and send
    const requestType = determineRequestType(message);
    
    try {
        let response;
        if (requestType === 'suggest') {
            response = await getSuggestions(url);
        } else if (requestType === 'question') {
            response = await askQuestion(url, message);
        } else {
            // Default to extraction
            response = await extractData(url, message);
        }
        
        removeLoadingMessage(loadingId);
        addAIMessage(response);
        
        // Save to history
        saveChatToHistory(url, message, response);
        
    } catch (error) {
        removeLoadingMessage(loadingId);
        addAIMessage({
            error: true,
            message: `Sorry, I encountered an error: ${error.message}`
        });
    } finally {
        // Re-enable input
        sendBtn.disabled = false;
        messageInput.disabled = false;
        urlInput.disabled = false;
        messageInput.focus();
    }
}

// Determine Request Type
function determineRequestType(message) {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('suggest') || lowerMessage.includes('what can') || 
        lowerMessage.includes('recommend')) {
        return 'suggest';
    } else if (lowerMessage.includes('?') || lowerMessage.includes('what') || 
               lowerMessage.includes('how') || lowerMessage.includes('why')) {
        return 'question';
    } else {
        return 'extract';
    }
}

// API Calls
async function askQuestion(url, question) {
    const response = await fetch('/api/jobs/ask_question/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, question })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
        return {
            type: 'answer',
            content: data.answer
        };
    } else {
        throw new Error(data.error || 'Failed to get answer');
    }
}

async function getSuggestions(url) {
    const response = await fetch('/api/jobs/get_suggestions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
        return {
            type: 'suggestions',
            content: data.suggestions
        };
    } else {
        throw new Error(data.error || 'Failed to get suggestions');
    }
}

async function extractData(url, instructions) {
    const response = await fetch('/api/jobs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url,
            user_instructions: instructions,
            scraper_type: 'auto'
        })
    });
    
    const data = await response.json();
    
    if (data.status === 'completed') {
        return {
            type: 'extraction',
            content: data.scraped_data,
            jobId: data.id
        };
    } else if (data.id) {
        // Job created, return job link
        return {
            type: 'job_created',
            jobId: data.id
        };
    } else {
        throw new Error('Failed to create scraping job');
    }
}

// Add Messages to Chat
function addUserMessage(message, url) {
    const messagesContainer = document.getElementById('chatMessages');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageHTML = `
        <div class="message user-message">
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <p>${escapeHtml(message)}</p>
                    <div class="url-badge">
                        <i class="fas fa-link"></i>
                        <span>${escapeHtml(url)}</span>
                    </div>
                </div>
                <div class="message-time">${time}</div>
            </div>
        </div>
    `;
    
    messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function addAIMessage(response) {
    const messagesContainer = document.getElementById('chatMessages');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let contentHTML = '';
    
    if (response.error) {
        contentHTML = `<p class="text-red-600"><i class="fas fa-exclamation-circle"></i> ${escapeHtml(response.message)}</p>`;
    } else if (response.type === 'answer') {
        contentHTML = `<p>${escapeHtml(response.content)}</p>`;
    } else if (response.type === 'suggestions') {
        contentHTML = '<p><strong>📌 I found these extractable fields:</strong></p><ul>';
        if (Array.isArray(response.content) && response.content.length > 0) {
            response.content.forEach(suggestion => {
                contentHTML += `<li><strong>${escapeHtml(suggestion.name || 'Field')}:</strong> ${escapeHtml(suggestion.description || '')}</li>`;
            });
        } else {
            contentHTML += '<li>No specific suggestions available for this page</li>';
        }
        contentHTML += '</ul>';
    } else if (response.type === 'extraction') {
        contentHTML = `
            <p>✅ <strong>Data extracted successfully!</strong></p>
            <p>I've scraped and processed the website. The data is now available.</p>
            <a href="/job/${response.jobId}/" class="view-results-link" target="_blank">
                <i class="fas fa-external-link-alt"></i> View Full Results
            </a>
        `;
    } else if (response.type === 'job_created') {
        contentHTML = `
            <p>⏳ <strong>Scraping job created!</strong></p>
            <p>Your scraping request is being processed.</p>
            <a href="/job/${response.jobId}/" class="view-results-link" target="_blank">
                <i class="fas fa-external-link-alt"></i> View Job Status
            </a>
        `;
    }
    
    const messageHTML = `
        <div class="message ai-message">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${contentHTML}
                </div>
                <div class="message-time">${time}</div>
            </div>
        </div>
    `;
    
    messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function addLoadingMessage() {
    const messagesContainer = document.getElementById('chatMessages');
    const loadingId = 'loading-' + Date.now();
    
    const loadingHTML = `
        <div class="message ai-message" id="${loadingId}">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="loading-message">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    messagesContainer.insertAdjacentHTML('beforeend', loadingHTML);
    scrollToBottom();
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingElement = document.getElementById(loadingId);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Quick Actions
function insertExample(type) {
    const urlInput = document.getElementById('chatUrl');
    const messageInput = document.getElementById('chatMessage');
    
    const examples = {
        question: {
            url: 'https://example.com',
            message: 'What is the main topic of this website?'
        },
        extract: {
            url: 'https://example.com',
            message: 'Extract the title, description, and all links from this page'
        },
        suggest: {
            url: 'https://example.com',
            message: 'What data can I extract from this page?'
        }
    };
    
    if (examples[type]) {
        urlInput.value = examples[type].url;
        messageInput.value = examples[type].message;
        messageInput.focus();
        autoResizeTextarea();
    }
}

// Clear Chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        const messagesContainer = document.getElementById('chatMessages');
        // Keep only the welcome message (first child)
        const welcomeMessage = messagesContainer.firstElementChild;
        messagesContainer.innerHTML = '';
        if (welcomeMessage) {
            messagesContainer.appendChild(welcomeMessage);
        }
    }
}

// History Management
function toggleHistory() {
    const sidebar = document.getElementById('historySidebar');
    sidebar.classList.toggle('active');
}

function saveChatToHistory(url, query, response) {
    const historyItem = {
        url,
        query,
        response,
        timestamp: new Date().toISOString()
    };
    
    chatHistory.unshift(historyItem);
    
    // Keep only last 20 items
    if (chatHistory.length > 20) {
        chatHistory = chatHistory.slice(0, 20);
    }
    
    // Save to localStorage
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    
    // Update history display
    updateHistoryDisplay();
}

function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        chatHistory = JSON.parse(saved);
        updateHistoryDisplay();
    }
}

function updateHistoryDisplay() {
    const historyList = document.getElementById('historyList');
    
    if (chatHistory.length === 0) {
        historyList.innerHTML = '<p class="text-gray-500 text-center p-4">No history yet</p>';
        return;
    }
    
    historyList.innerHTML = chatHistory.map((item, index) => {
        const date = new Date(item.timestamp);
        const timeAgo = getTimeAgo(date);
        
        return `
            <div class="history-item" onclick="loadHistoryItem(${index})">
                <div class="history-item-url">${escapeHtml(item.url)}</div>
                <div class="history-item-query">${escapeHtml(item.query.substring(0, 60))}${item.query.length > 60 ? '...' : ''}</div>
                <div class="history-item-time">${timeAgo}</div>
            </div>
        `;
    }).join('');
}

function loadHistoryItem(index) {
    const item = chatHistory[index];
    if (item) {
        document.getElementById('chatUrl').value = item.url;
        document.getElementById('chatMessage').value = item.query;
        autoResizeTextarea();
        toggleHistory();
    }
}

// Utility Functions
function scrollToBottom() {
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'Just now';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                z-index: 9999;
                animation: slideInRight 0.3s ease;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .notification-error {
                border-left: 4px solid #f56565;
                color: #c53030;
            }
            
            .notification-success {
                border-left: 4px solid #48bb78;
                color: #2f855a;
            }
            
            .notification-warning {
                border-left: 4px solid #ed8936;
                color: #c05621;
            }
            
            .notification-info {
                border-left: 4px solid #4299e1;
                color: #2c5282;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS for view results link
const style = document.createElement('style');
style.textContent = `
    .view-results-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.75rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .view-results-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
`;
document.head.appendChild(style);