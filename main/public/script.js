const API_URL = '/entries';
let allEntries = [];
let editingId = null;
let activeFilter = null; // tracks the active phase filter tag

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

function renderEntries(entries) {
    if (entries.length === 0) {
        grid.innerHTML = `<div class="loader">No matching lessons found. Try a different search.</div>`;
        return;
    }

    grid.innerHTML = entries.map(entry => `
        <article class="card">
            <div class="card-header">
                <div class="header-main">
                    <h3 class="equipment-name">${entry.equipment_system} ${entry.model_number ? `<span style="font-size: 0.9rem; font-weight: 300; opacity: 0.7; margin-left: 0.5rem;">(${entry.model_number})</span>` : ''}</h3>
                    <div class="project-name">${entry.project_name} | <span class="consultant-name" style="color: var(--text-primary); font-weight: 500;">${entry.consultant}</span></div>
                </div>
                <div class="header-actions">
                    <span class="phase-badge">${entry.validation_phase}</span>
                    <button class="btn-edit" onclick="editEntry('${entry.id}')" title="Edit Entry">✎</button>
                    <button class="btn-delete" onclick="deleteEntry('${entry.id}')" title="Delete Entry">&times;</button>
                </div>
            </div>
            
            <div class="card-body">
                ${entry.intended_outcome ? `
                    <h4>Intended Outcome</h4>
                    <p>${entry.intended_outcome}</p>
                ` : ''}
                
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
                ${entry.attachments ? `<a href="${entry.attachments}" target="_blank" class="attachment-link">📎 View Files</a>` : ''}
            </div>
        </article>
    `).join('');
}

// Global Delete Function
async function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this validation lesson? This cannot be undone.')) return;
    
    try {
        const response = await fetch(`/entries/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadEntries(); // Refresh the grid
        }
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
    
    // Fill form
    document.getElementById('project_name').value = entry.project_name;
    document.getElementById('consultant').value = entry.consultant;
    document.getElementById('equipment_system').value = entry.equipment_system;
    document.getElementById('model_number').value = entry.model_number || '';
    document.getElementById('validation_phase').value = entry.validation_phase;
    document.getElementById('intended_outcome').value = entry.intended_outcome;
    document.getElementById('obstacle').value = entry.obstacle;
    document.getElementById('resolution').value = entry.resolution;
    document.getElementById('date_logged').value = entry.date_logged;
    document.getElementById('attachments').value = entry.attachments || '';
    document.getElementById('keywords').value = entry.keywords.join(', ');

    openModal();
}


// Search & Filter Logic
function handleSearch() {
    const query = searchInput.value.toLowerCase();

    const filtered = allEntries.filter(entry => {
        // Text search across multiple fields
        const matchesText = !query ||
            entry.equipment_system.toLowerCase().includes(query) ||
            (entry.model_number && entry.model_number.toLowerCase().includes(query)) ||
            entry.project_name.toLowerCase().includes(query) ||
            entry.keywords.some(kw => kw.toLowerCase().includes(query)) ||
            entry.obstacle.toLowerCase().includes(query) ||
            entry.validation_phase.toLowerCase().includes(query);

        // Phase filter tag
        let matchesPhase = true;
        if (activeFilter === 'Others') {
            matchesPhase = !STANDARD_PHASES.includes(entry.validation_phase);
        } else if (activeFilter) {
            matchesPhase = entry.validation_phase === activeFilter;
        }

        return matchesText && matchesPhase;
    });

    renderEntries(filtered);
}

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

    // Load draft if it exists
    const draft = localStorage.getItem('lesson_draft');
    if (draft) {
        const data = JSON.parse(draft);
        fillForm(data);
    } else {
        form.reset();
        document.getElementById('date_logged').value = new Date().toISOString().split('T')[0];
    }

    openModal();
};

function fillForm(data) {
    document.getElementById('project_name').value = data.project_name || '';
    document.getElementById('consultant').value = data.consultant || '';
    document.getElementById('equipment_system').value = data.equipment_system || '';
    document.getElementById('model_number').value = data.model_number || '';
    document.getElementById('validation_phase').value = data.validation_phase || 'URS';
    document.getElementById('intended_outcome').value = data.intended_outcome || '';
    document.getElementById('obstacle').value = data.obstacle || '';
    document.getElementById('resolution').value = data.resolution || '';
    document.getElementById('date_logged').value = data.date_logged || new Date().toISOString().split('T')[0];
    document.getElementById('attachments').value = data.attachments || '';
    document.getElementById('keywords').value = Array.isArray(data.keywords) ? data.keywords.join(', ') : (data.keywords || '');
}

// Auto-save draft as the user types
form.addEventListener('input', () => {
    if (editingId) return; // Don't save drafts when editing existing entries
    
    const draftData = {
        project_name: document.getElementById('project_name').value,
        consultant: document.getElementById('consultant').value,
        equipment_system: document.getElementById('equipment_system').value,
        model_number: document.getElementById('model_number').value,
        validation_phase: document.getElementById('validation_phase').value,
        intended_outcome: document.getElementById('intended_outcome').value,
        obstacle: document.getElementById('obstacle').value,
        resolution: document.getElementById('resolution').value,
        date_logged: document.getElementById('date_logged').value,
        attachments: document.getElementById('attachments').value,
        keywords: document.getElementById('keywords').value
    };
    localStorage.setItem('lesson_draft', JSON.stringify(draftData));
});

closeBtn.onclick = () => {
    if (!editingId && formHasContent() && !confirm('You have unsaved changes. Close anyway?')) return;
    closeModal();
};

// Check if form has content to prevent accidental data loss
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
    
    const formData = {
        project_name: document.getElementById('project_name').value,
        consultant: document.getElementById('consultant').value,
        equipment_system: document.getElementById('equipment_system').value,
        model_number: document.getElementById('model_number').value,
        validation_phase: document.getElementById('validation_phase').value,
        intended_outcome: document.getElementById('intended_outcome').value,
        obstacle: document.getElementById('obstacle').value,
        resolution: document.getElementById('resolution').value,
        date_logged: document.getElementById('date_logged').value,
        attachments: document.getElementById('attachments').value,
        keywords: document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k !== "")
    };

    const url = editingId ? `${API_URL}/${editingId}` : API_URL;
    const method = editingId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
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
            // Clicking the same tag again clears the filter
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
