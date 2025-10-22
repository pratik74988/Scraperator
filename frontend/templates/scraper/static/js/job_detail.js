// ============================================
// Job Detail Page JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initAIDataView();
    formatJSON();
    setupAutoRefresh();
});
// --- Initialize AI Data View ---
function initAIDataView() {
    const aiDataElement = document.getElementById('aiDataJSON');
    //if (!aiDataElement) return;

    try {
        const aiData = JSON.parse(aiDataElement.textContent);
        renderCardView(aiData);
        renderStructuredView(aiData);
        setupViewToggle();
    } catch (error) {
        console.error("Failed to parse AI data:", error);
    }
}

// --- Render Card View ---
function renderCardView(data) {
    const container = document.getElementById('cardView');
    if (!container) return;
    container.innerHTML = '';

    if (data.benefit_schemes && Array.isArray(data.benefit_schemes)) {
        data.benefit_schemes.forEach(item => container.appendChild(createCard(item)));
    } else if (Array.isArray(data)) {
        data.forEach(item => container.appendChild(createCard(item)));
    } else if (typeof data === 'object') {
        Object.entries(data).forEach(([key, value]) =>
            container.appendChild(createCardFromKeyValue(key, value))
        );
    } else {
        container.innerHTML = `<div class="text-gray-600 italic">No data to display in card view.</div>`;
    }
}

// --- Create Card from Item ---
function createCard(item) {
    const card = document.createElement('div');
    card.className = 'extracted-card';

    if (item.name) {
        card.innerHTML = `
            <h4>${escapeHtml(item.name)}</h4>
            ${item.department ? `<p>Dept: ${escapeHtml(item.department)}</p>` : ''}
            ${item.description ? `<p>${escapeHtml(item.description)}</p>` : ''}
        `;
    } else if (item.title) {
        card.innerHTML = `
            <h4>${escapeHtml(item.title)}</h4>
            ${item.content ? `<p>${escapeHtml(item.content)}</p>` : ''}
        `;
    } else {
        card.innerHTML = `<pre>${escapeHtml(JSON.stringify(item, null, 2))}</pre>`;
    }
    return card;
}

// --- Create Card for Generic Key-Value Pair ---
function createCardFromKeyValue(key, value) {
    const card = document.createElement('div');
    card.className = 'extracted-card';
    card.innerHTML = `
        <h4>${escapeHtml(key)}</h4>
        <p>${escapeHtml(JSON.stringify(value, null, 2))}</p>
    `;
    return card;
}

// --- Render Structured View ---
function renderStructuredView(data) {
    const structured = document.getElementById('structuredData');
    if (structured) structured.textContent = JSON.stringify(data, null, 2);
}

// --- Setup Toggle Buttons ---
function setupViewToggle() {
    const cardBtn = document.getElementById("cardViewBtn");
    const structuredBtn = document.getElementById("structuredViewBtn");
    const cardContainer = document.getElementById("cardView");
    const structuredContainer = document.getElementById("structuredView");

    cardBtn.addEventListener("click", () => {
        cardContainer.classList.remove("hidden");
        structuredContainer.classList.add("hidden");
        toggleActive(cardBtn, structuredBtn);
    });

    structuredBtn.addEventListener("click", () => {
        structuredContainer.classList.remove("hidden");
        cardContainer.classList.add("hidden");
        toggleActive(structuredBtn, cardBtn);
    });
}

// --- Helper: Toggle Active Button ---
function toggleActive(active, inactive) {
    active.classList.add("bg-purple-600", "text-white");
    active.classList.remove("bg-gray-200", "text-gray-700");

    inactive.classList.add("bg-gray-200", "text-gray-700");
    inactive.classList.remove("bg-purple-600", "text-white");
}

// --- Escape HTML ---
function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str.replace(/[&<>"']/g, m => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[m]));
}

// Run when DOM is ready
document.addEventListener("DOMContentLoaded", initAIDataView);
