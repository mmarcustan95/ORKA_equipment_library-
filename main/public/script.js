const API_URL = '/entries';
let allEntries = [];

// DOM Elements
const grid = document.getElementById('entries-grid');
const searchInput = document.getElementById('search-input');
const modal = document.getElementById('entry-modal');
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
                <span class="phase-badge">${entry.validation_phase}</span>
            </div>
            <div class="project-name">${entry.project_name}</div>
            
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
                <div class="keywords-list">
                    ${entry.keywords.map(kw => `<span class="keyword-pill">${kw}</span>`).join('')}
                </div>
            </div>
        </article>
    `).join('');
}

// Search & Filter Logic
function handleSearch() {
    const query = searchInput.value.toLowerCase();
    const filtered = allEntries.filter(entry => 
        entry.equipment_system.toLowerCase().includes(query) ||
        entry.project_name.toLowerCase().includes(query) ||
        entry.keywords.some(kw => kw.toLowerCase().includes(query)) ||
        entry.obstacle.toLowerCase().includes(query)
    );
    renderEntries(filtered);
}

// Modal Toggle
addBtn.onclick = () => modal.style.display = 'block';
closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

// Form Submission
form.onsubmit = async (e) => {
    e.preventDefault();
    
    const formData = {
        project_name: document.getElementById('project_name').value,
        equipment_system: document.getElementById('equipment_system').value,
        validation_phase: document.getElementById('validation_phase').value,
        intended_outcome: document.getElementById('intended_outcome').value,
        obstacle: document.getElementById('obstacle').value,
        resolution: document.getElementById('resolution').value,
        date_logged: document.getElementById('date_logged').value,
        keywords: document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k !== "")
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            form.reset();
            modal.style.display = 'none';
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
        searchInput.value = filter;
        handleSearch();
    };
});

searchInput.addEventListener('input', handleSearch);

// Initialize
loadEntries();
