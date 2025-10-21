// ============================================
// Create Job Page JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    setupFormSubmission();
});

// Setup form submission handler
function setupFormSubmission() {
    const form = document.getElementById('scrapeForm');
    form.addEventListener('submit', handleFormSubmit);
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    
    // Get form data
    const formData = {
        url: document.getElementById('url').value,
        user_instructions: document.getElementById('user_instructions').value,
        scraper_type: document.getElementById('scraper_type').value
    };
    
    // Show loading state
    submitBtn.disabled = true;
    loadingState.classList.remove('hidden');
    errorState.classList.add('hidden');
    
    try {
        const response = await fetch('/api/jobs/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.id) {
            // Redirect to job detail page
            window.location.href = `/job/${data.id}/`;
        } else {
            throw new Error(data.error || 'Failed to create scrape job');
        }
    } catch (error) {
        // Show error
        errorState.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = error.message;
        submitBtn.disabled = false;
        loadingState.classList.add('hidden');
    }
}

// Get AI suggestions for the URL
async function getSuggestions() {
    const urlInput = document.getElementById('url');
    const url = urlInput.value.trim();
    
    if (!url) {
        alert('Please enter a URL first');
        return;
    }
    
    if (!isValidUrl(url)) {
        alert('Please enter a valid URL');
        return;
    }
    
    const suggestionsBox = document.getElementById('suggestionsBox');
    const suggestionsContent = document.getElementById('suggestionsContent');
    
    // Show loading in suggestions box
    suggestionsBox.classList.remove('hidden');
    suggestionsContent.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="spinner"></div>
            <span>Analyzing website...</span>
        </div>
    `;
    
    try {
        const response = await fetch('/api/jobs/get_suggestions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.status === 'success' && data.suggestions) {
            displaySuggestions(data.suggestions);
        } else {
            throw new Error(data.error || 'Failed to get suggestions');
        }
    } catch (error) {
        suggestionsContent.innerHTML = `
            <p style="color: #dc2626;">Error: ${error.message}</p>
        `;
    }
}

// Display suggestions
function displaySuggestions(suggestions) {
    const suggestionsContent = document.getElementById('suggestionsContent');
    
    if (!Array.isArray(suggestions) || suggestions.length === 0) {
        suggestionsContent.innerHTML = `
            <p style="color: #6b7280;">No specific suggestions available for this URL</p>
        `;
        return;
    }
    
    suggestionsContent.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item" onclick="useSuggestion('${escapeHtml(suggestion.name)}', '${escapeHtml(suggestion.description)}')">
            <p class="suggestion-name">📌 ${escapeHtml(suggestion.name || 'Field')}</p>
            <p class="suggestion-desc">${escapeHtml(suggestion.description || '')}</p>
            <p class="suggestion-hint">Click to use this suggestion</p>
        </div>
    `).join('');
}

// Use a suggestion
function useSuggestion(name, description) {
    const instructionsInput = document.getElementById('user_instructions');
    instructionsInput.value = `Extract: ${name} - ${description}`;
    instructionsInput.focus();
}

// Validate URL
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}