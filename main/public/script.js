const API_URL = '/entries';
let allEntries = [];
let editingId = null;
let activeFilter = null;

const STANDARD_PHASES = ['URS', 'FAT', 'SAT', 'IQ', 'OQ', 'PQ'];

// DOM Elements
const grid = document.getElementById('entries-grid');
const searchInput = document.getElementById('search-input');
const modal = document.getElementById('entry-modal');
const modalTitle = modal.querySelector('h2');
const addBtn = document.getElementById('add-entry-btn');
const closeBtn = document.querySelector('.close-modal');
const form = document.getElementById('entry-form');
const filterTags = document.querySelectorAll('.filter-tag');

// Fetch and render data
async function loadEntries() {
    try {
        const response = await fetch(API_URL);
        allEntries = await response.json();
        renderEntries(allEntries);
    } catch (error) {
        console.error('Error loading entries:', error);
        grid.innerHTML = `<div class="loader" style="color: var(--danger)">Failed to load data. Make sure the server is running.</div>`;
    }
}

// --- Card rendering helpers ---

function renderModelNumber(modelNumber) {
    if (!modelNumber) return '';
    return `<span style="font-size: 0.9rem; font-weight: 300; opacity: 0.7; margin-left: 0.5rem;">(${modelNumber})</span>`;
}

function renderOutcome(outcome) {
    if (!outcome) return '';
    return `<h4>Intended Outcome</h4><p>${outcome}</p>`;
}

function renderAttachment(attachments) {
    if (!attachments) return '';
    return `<a href="${attachments}" target="_blank" class="attachment-link">📎 View Files</a>`;
}

function renderCard(entry) {
    return `
        <article class="card">
            <div class="card-header">
                <div class="header-main">
                    <h3 class="equipment-name">${entry.equipment_system} ${renderModelNumber(entry.model_number)}</h3>
                    <div class="project-name">${entry.project_name} | <span class="consultant-name" style="color: var(--text-primary); font-weight: 500;">${entry.consultant}</span></div>
                </div>
                <div class="header-actions">
                    <span class="phase-badge">${entry.validation_phase}</span>
                    <button class="btn-edit" onclick="editEntry('${entry.id}')" title="Edit Entry">✎</button>
                    <button class="btn-delete" onclick="deleteEntry('${entry.id}')" title="Delete Entry">&times;</button>
                </div>
            </div>
            <div class="card-body">
                ${renderOutcome(entry.intended_outcome)}
                <div class="obstacle-box">
                    <h4>Obstacle Encountered</h4>
                    <p>${entry.obstacle}</p>
                </div>
                <div class="resolution-box">
                    <h4>Resolution / Learning</h4>
                    <p>${entry.resolution}</p>
                </div>
            </div>
            <div class="card-footer">
                <div class="footer-left">
                    <span class="date">${new Date(entry.date_logged).toLocaleDateString()}</span>
                    <div class="keywords-list">
                        ${entry.keywords.map(kw => `<span class="keyword-pill">${kw}</span>`).join('')}
                    </div>
                </div>
                ${renderAttachment(entry.attachments)}
            </div>
        </article>
    `;
}

function renderEntries(entries) {
    if (entries.length === 0) {
        grid.innerHTML = `<div class="loader">No matching lessons found. Try a different search.</div>`;
        return;
    }
    grid.innerHTML = entries.map(renderCard).join('');
}

// Global Delete Function
async function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this validation lesson? This cannot be undone.')) return;
    try {
        const response = await fetch(`/entries/${id}`, { method: 'DELETE' });
        if (response.ok) loadEntries();
    } catch (error) {
        console.error('Error deleting entry:', error);
        alert('Failed to delete entry.');
    }
}

// Global Edit Function
function editEntry(id) {
    const entry = allEntries.find(e => e.id === id);
    if (!entry) return;
    editingId = id;
    modalTitle.textContent = 'Edit Validation Lesson';
    fillForm(entry);
    openModal();
}

// --- Search & filter helpers ---

function entryMatchesText(entry, query) {
    if (!query) return true;
    return (
        entry.equipment_system.toLowerCase().includes(query) ||
        (entry.model_number && entry.model_number.toLowerCase().includes(query)) ||
        entry.project_name.toLowerCase().includes(query) ||
        entry.keywords.some(kw => kw.toLowerCase().includes(query)) ||
        entry.obstacle.toLowerCase().includes(query) ||
        entry.validation_phase.toLowerCase().includes(query)
    );
}

function entryMatchesPhase(entry) {
    if (activeFilter === 'Others') return !STANDARD_PHASES.includes(entry.validation_phase);
    if (activeFilter) return entry.validation_phase === activeFilter;
    return true;
}

function handleSearch() {
    const query = searchInput.value.toLowerCase();
    const filtered = allEntries.filter(entry =>
        entryMatchesText(entry, query) && entryMatchesPhase(entry)
    );
    renderEntries(filtered);
}

// Modal helpers
function openModal() {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

// Modal Toggle
addBtn.onclick = () => {
    editingId = null;
    modalTitle.textContent = 'Log Validation Lesson Learned';
    const draft = localStorage.getItem('lesson_draft');
    if (draft) {
        fillForm(JSON.parse(draft));
    } else {
        form.reset();
        document.getElementById('date_logged').value = new Date().toISOString().split('T')[0];
    }
    openModal();
};

// --- Form helpers ---

function normalizeKeywords(keywords) {
    if (Array.isArray(keywords)) return keywords.join(', ');
    return keywords || '';
}

function fillForm(data) {
    const today = new Date().toISOString().split('T')[0];
    const fields = {
        project_name:      data.project_name || '',
        consultant:        data.consultant || '',
        equipment_system:  data.equipment_system || '',
        model_number:      data.model_number || '',
        validation_phase:  data.validation_phase || 'URS',
        intended_outcome:  data.intended_outcome || '',
        obstacle:          data.obstacle || '',
        resolution:        data.resolution || '',
        date_logged:       data.date_logged || today,
        attachments:       data.attachments || '',
        keywords:          normalizeKeywords(data.keywords),
    };
    Object.entries(fields).forEach(([id, value]) => {
        document.getElementById(id).value = value;
    });
}

function getFormData() {
    return {
        project_name:      document.getElementById('project_name').value,
        consultant:        document.getElementById('consultant').value,
        equipment_system:  document.getElementById('equipment_system').value,
        model_number:      document.getElementById('model_number').value,
        validation_phase:  document.getElementById('validation_phase').value,
        intended_outcome:  document.getElementById('intended_outcome').value,
        obstacle:          document.getElementById('obstacle').value,
        resolution:        document.getElementById('resolution').value,
        date_logged:       document.getElementById('date_logged').value,
        attachments:       document.getElementById('attachments').value,
        keywords:          document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k !== ''),
    };
}

// Auto-save draft as the user types
form.addEventListener('input', () => {
    if (editingId) return;
    const draft = getFormData();
    draft.keywords = document.getElementById('keywords').value;
    localStorage.setItem('lesson_draft', JSON.stringify(draft));
});

closeBtn.onclick = () => {
    if (!editingId && formHasContent() && !confirm('You have unsaved changes. Close anyway?')) return;
    closeModal();
};

function formHasContent() {
    const inputs = ['project_name', 'consultant', 'equipment_system', 'intended_outcome', 'obstacle', 'resolution'];
    return inputs.some(id => document.getElementById(id).value.trim() !== '');
}

window.onclick = (e) => {
    if (e.target == modal) {
        if (!editingId && formHasContent() && !confirm('You have unsaved changes. Close anyway?')) return;
        closeModal();
    }
};

// Form Submission
form.onsubmit = async (e) => {
    e.preventDefault();
    const url = editingId ? `${API_URL}/${editingId}` : API_URL;
    const method = editingId ? 'PUT' : 'POST';
    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(getFormData()),
        });
        if (response.ok) {
            form.reset();
            localStorage.removeItem('lesson_draft');
            closeModal();
            editingId = null;
            loadEntries();
        }
    } catch (error) {
        console.error('Error submitting entry:', error);
        alert('Failed to save entry. Check console for details.');
    }
};

// Filter tags
filterTags.forEach(tag => {
    tag.onclick = () => {
        const filter = tag.getAttribute('data-filter');
        if (activeFilter === filter) {
            activeFilter = null;
            tag.classList.remove('active');
        } else {
            activeFilter = filter;
            filterTags.forEach(t => t.classList.remove('active'));
            tag.classList.add('active');
        }
        handleSearch();
    };
});

searchInput.addEventListener('input', handleSearch);

// Initialize
loadEntries();
