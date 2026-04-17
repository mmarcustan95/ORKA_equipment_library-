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
                <h3 class="equipment-name">${entry.equipment_system}</h3>
                <div class="header-actions">
                    <span class="phase-badge">${entry.validation_phase}</span>
                    <button class="btn-edit" onclick="editEntry('${entry.id}')" title="Edit Entry">✎</button>
                    <button class="btn-delete" onclick="deleteEntry('${entry.id}')" title="Delete Entry">&times;</button>
                </div>
            </div>
            <div class="project-name">${entry.project_name} | <span class="consultant-name">${entry.consultant}</span></div>
            
            <div class="card-body">
                <h4>Obstacle</h4>
                <p>${entry.obstacle}</p>
                
                <div class="resolution-box">
                    <h4>Resolution</h4>
                    <p>${entry.resolution}</p>
                </div>
            </div>
            
            <div class="card-footer">
                <span class="date">${new Date(entry.date_logged).toLocaleDateString()}</span>
                ${entry.attachments ? `<a href="${entry.attachments}" target="_blank" class="attachment-link">📎 View Files</a>` : ''}
                <div class="keywords-list">
                    ${entry.keywords.map(kw => `<span class="keyword-pill">${kw}</span>`).join('')}
                </div>
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
    document.getElementById('validation_phase').value = entry.validation_phase;
    document.getElementById('intended_outcome').value = entry.intended_outcome;
    document.getElementById('obstacle').value = entry.obstacle;
    document.getElementById('resolution').value = entry.resolution;
    document.getElementById('date_logged').value = entry.date_logged;
    document.getElementById('attachments').value = entry.attachments || '';
    document.getElementById('keywords').value = entry.keywords.join(', ');

    modal.style.display = 'block';
}


// Search & Filter Logic
function handleSearch() {
    const query = searchInput.value.toLowerCase();

    const filtered = allEntries.filter(entry => {
        // Text search across multiple fields
        const matchesText = !query ||
            entry.equipment_system.toLowerCase().includes(query) ||
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

// Modal Toggle
addBtn.onclick = () => {
    editingId = null;
    modalTitle.textContent = 'Log Validation Lesson Learned';
    form.reset();
    modal.style.display = 'block';
};

closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

// Form Submission
form.onsubmit = async (e) => {
    e.preventDefault();
    
    const formData = {
        project_name: document.getElementById('project_name').value,
        consultant: document.getElementById('consultant').value,
        equipment_system: document.getElementById('equipment_system').value,
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
            modal.style.display = 'none';
            editingId = null;
            loadEntries(); // Refresh the grid
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
