const API_URL = '/entries';
let allEntries = [];
let editingId = null;
let selectedId = null;
let activeFilter = null;
let activeConsultant = '';
let activeKeyword = null;
let sortOrder = 'newest';
let dateFrom = null;
let dateTo = null;

const STANDARD_PHASES = ['URS', 'FAT', 'SAT', 'IQ', 'OQ', 'PQ'];
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

const grid = document.getElementById('entries-grid');
const detailPane = document.getElementById('detail-pane');
const searchInput = document.getElementById('search-input');
const modal = document.getElementById('entry-modal');
const modalTitle = modal.querySelector('h2');
const addBtn = document.getElementById('add-entry-btn');
const closeBtn = document.querySelector('.close-modal');
const form = document.getElementById('entry-form');
const filterTags = document.querySelectorAll('.filter-tag');
const consultantFilter = document.getElementById('consultant-filter');
const sortSelect = document.getElementById('sort-select');
const dateFromInput = document.getElementById('date-from');
const dateToInput = document.getElementById('date-to');
const exportBtn = document.getElementById('export-csv-btn');
const entryCountEl = document.getElementById('entry-count');

async function loadEntries() {
    try {
        const response = await fetch(API_URL);
        allEntries = await response.json();
        populateConsultantFilter();
        updateStats();
        restoreFromURL();
        const visible = getSortedEntries(getFilteredEntries());
        if (!selectedId || !allEntries.some(e => String(e.id) === String(selectedId))) {
            selectedId = visible[0] ? String(visible[0].id) : null;
        }
        renderEntries(visible);
    } catch (error) {
        console.error('Error loading entries:', error);
        grid.innerHTML = '<div class="loader" style="color: var(--red-500)">Failed to load data. Make sure the server is running.</div>';
        renderDetail(null);
    }
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function populateConsultantFilter() {
    const current = consultantFilter.value;
    const consultants = [...new Set(allEntries.map(e => e.consultant).filter(Boolean))].sort();
    consultantFilter.innerHTML = '<option value="">All Consultants</option>';
    consultants.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        consultantFilter.appendChild(opt);
    });
    consultantFilter.value = current;
}

function updateStats() {
    const phaseCounts = {};
    const consultantSet = new Set();
    allEntries.forEach(e => {
        phaseCounts[e.validation_phase] = (phaseCounts[e.validation_phase] || 0) + 1;
        if (e.consultant) consultantSet.add(e.consultant);
    });
    const topPhase = Object.entries(phaseCounts).sort((a, b) => b[1] - a[1])[0];
    document.getElementById('stat-total').textContent = allEntries.length;
    document.getElementById('stat-consultants').textContent = consultantSet.size;
    document.getElementById('stat-top-phase').textContent = topPhase ? topPhase[0] : '-';
}

function isNew(entry) {
    const logged = new Date(entry.date_logged).getTime();
    return Number.isFinite(logged) && (Date.now() - logged) < SEVEN_DAYS_MS;
}

function renderMasterItem(entry) {
    const id = String(entry.id);
    const selected = id === String(selectedId);
    const newBadge = isNew(entry) ? '<span class="new-badge">New</span>' : '';
    return `
        <article class="master-item${selected ? ' selected' : ''}" data-id="${escapeHtml(id)}" tabindex="0">
            <div class="master-top">
                <div class="master-title">${escapeHtml(entry.equipment_system)}</div>
                <div class="master-badges">
                    ${newBadge}
                    <span class="phase-badge">${escapeHtml(entry.validation_phase)}</span>
                </div>
            </div>
            <div class="master-meta">${escapeHtml(entry.project_name)} - ${escapeHtml(entry.consultant)}</div>
        </article>
    `;
}

function renderEntries(entries) {
    entryCountEl.textContent = `Showing ${entries.length} of ${allEntries.length} entries`;
    grid.innerHTML = entries.length
        ? entries.map(renderMasterItem).join('')
        : '<div class="loader">No matching lessons found. Try a different search.</div>';

    grid.querySelectorAll('.master-item').forEach(item => {
        item.addEventListener('click', () => selectEntry(item.dataset.id));
        item.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                selectEntry(item.dataset.id);
            }
        });
    });

    const selected = entries.find(e => String(e.id) === String(selectedId));
    renderDetail(selected || null);
}

function renderModelNumber(modelNumber) {
    return modelNumber ? `<span class="model-number">(${escapeHtml(modelNumber)})</span>` : '';
}

function renderAttachment(attachments) {
    return attachments ? `<a href="${escapeHtml(attachments)}" target="_blank" rel="noopener" class="attachment-link">View Files -></a>` : '';
}

function renderKeywords(entry) {
    return (entry.keywords || []).map(kw => {
        const active = activeKeyword && kw.toLowerCase() === activeKeyword.toLowerCase();
        return `<button class="keyword-pill${active ? ' active' : ''}" type="button" data-keyword="${escapeHtml(kw)}">${escapeHtml(kw)}</button>`;
    }).join('');
}

function renderDetail(entry) {
    if (!entry) {
        detailPane.innerHTML = `
            <div class="empty-state">
                <span class="search-icon">Q</span>
                <span>Select a lesson to view details</span>
            </div>
        `;
        return;
    }

    detailPane.innerHTML = `
        <div class="detail-header">
            <h1 class="detail-title">${escapeHtml(entry.equipment_system)}${renderModelNumber(entry.model_number)}</h1>
            <div class="detail-actions">
                <span class="phase-badge">${escapeHtml(entry.validation_phase)}</span>
                <button class="icon-button" type="button" id="edit-selected" title="Edit lesson" aria-label="Edit lesson">Edit</button>
                <button class="icon-button" type="button" id="delete-selected" title="Delete lesson" aria-label="Delete lesson">&times;</button>
            </div>
        </div>
        <div class="detail-meta">${escapeHtml(entry.project_name)} | <strong>${escapeHtml(entry.consultant)}</strong></div>
        <div class="detail-date">Logged ${new Date(entry.date_logged).toLocaleDateString()}</div>

        ${entry.intended_outcome ? `
            <section class="detail-section">
                <div class="overline">Intended Outcome</div>
                <p>${escapeHtml(entry.intended_outcome)}</p>
            </section>
        ` : ''}

        <section class="detail-box obstacle-box">
            <div class="overline">Obstacle Encountered</div>
            <p>${escapeHtml(entry.obstacle)}</p>
        </section>

        <section class="detail-box resolution-box">
            <div class="overline">Resolution / Learning</div>
            <p>${escapeHtml(entry.resolution)}</p>
        </section>

        <div class="detail-footer">
            <div class="keywords-list">${renderKeywords(entry)}</div>
            ${renderAttachment(entry.attachments)}
        </div>
    `;

    document.getElementById('edit-selected').addEventListener('click', () => editEntry(entry.id));
    document.getElementById('delete-selected').addEventListener('click', () => deleteEntry(entry.id));
    detailPane.querySelectorAll('.keyword-pill').forEach(pill => {
        pill.addEventListener('click', () => filterByKeyword(pill.dataset.keyword));
    });
}

function selectEntry(id) {
    selectedId = String(id);
    applyFilters(false);
}

function filterByKeyword(kw) {
    activeKeyword = activeKeyword === kw ? null : kw;
    if (activeKeyword) searchInput.value = '';
    applyFilters();
    updateURL();
}

function getSortedEntries(entries) {
    return [...entries].sort((a, b) => {
        switch (sortOrder) {
            case 'oldest':
                return new Date(a.date_logged) - new Date(b.date_logged);
            case 'equipment':
                return a.equipment_system.localeCompare(b.equipment_system);
            case 'project':
                return a.project_name.localeCompare(b.project_name);
            default:
                return new Date(b.date_logged) - new Date(a.date_logged);
        }
    });
}

function getFilteredEntries() {
    const query = searchInput.value.toLowerCase();
    return allEntries.filter(entry => {
        if (!entryMatchesText(entry, query)) return false;
        if (activeFilter === 'Others' ? STANDARD_PHASES.includes(entry.validation_phase) : activeFilter && entry.validation_phase !== activeFilter) return false;
        if (activeConsultant && entry.consultant !== activeConsultant) return false;
        if (activeKeyword && !(entry.keywords || []).some(kw => kw.toLowerCase() === activeKeyword.toLowerCase())) return false;
        if (dateFrom || dateTo) {
            const d = new Date(entry.date_logged);
            if (dateFrom && d < new Date(dateFrom)) return false;
            if (dateTo && d > new Date(dateTo + 'T23:59:59')) return false;
        }
        return true;
    });
}

function entryMatchesText(entry, query) {
    if (!query) return true;
    return (
        entry.equipment_system.toLowerCase().includes(query) ||
        (entry.model_number && entry.model_number.toLowerCase().includes(query)) ||
        entry.project_name.toLowerCase().includes(query) ||
        (entry.keywords || []).some(kw => kw.toLowerCase().includes(query)) ||
        entry.obstacle.toLowerCase().includes(query) ||
        entry.resolution.toLowerCase().includes(query) ||
        entry.validation_phase.toLowerCase().includes(query)
    );
}

function applyFilters(keepFirstVisible = true) {
    const entries = getSortedEntries(getFilteredEntries());
    if (keepFirstVisible && (!selectedId || !entries.some(e => String(e.id) === String(selectedId)))) {
        selectedId = entries[0] ? String(entries[0].id) : null;
    }
    renderEntries(entries);
}

function updateURL() {
    const params = new URLSearchParams();
    if (searchInput.value) params.set('search', searchInput.value);
    if (activeFilter) params.set('phase', activeFilter);
    if (activeConsultant) params.set('consultant', activeConsultant);
    if (activeKeyword) params.set('keyword', activeKeyword);
    if (sortOrder !== 'newest') params.set('sort', sortOrder);
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    const qs = params.toString();
    history.replaceState(null, '', qs ? `${location.pathname}?${qs}` : location.pathname);
}

function restoreFromURL() {
    const params = new URLSearchParams(location.search);
    const search = params.get('search');
    const phase = params.get('phase');
    const consultant = params.get('consultant');
    const keyword = params.get('keyword');
    const sort = params.get('sort');
    const from = params.get('from');
    const to = params.get('to');

    if (search) searchInput.value = search;
    if (phase) {
        activeFilter = phase;
        filterTags.forEach(t => t.classList.toggle('active', t.getAttribute('data-filter') === phase));
    }
    if (consultant) {
        activeConsultant = consultant;
        consultantFilter.value = consultant;
    }
    if (keyword) activeKeyword = keyword;
    if (sort) {
        sortOrder = sort;
        sortSelect.value = sort;
    }
    if (from) {
        dateFrom = from;
        dateFromInput.value = from;
    }
    if (to) {
        dateTo = to;
        dateToInput.value = to;
    }
}

function exportCSV() {
    const rows = getSortedEntries(getFilteredEntries()).map(e => [
        e.date_logged, e.project_name, e.consultant, e.equipment_system,
        e.model_number || '', e.validation_phase, e.intended_outcome || '',
        e.obstacle, e.resolution, (e.keywords || []).join('; '), e.attachments || ''
    ].map(v => `"${String(v).replace(/"/g, '""')}"`));

    const headers = ['Date', 'Project', 'Consultant', 'Equipment', 'Model', 'Phase',
        'Intended Outcome', 'Obstacle', 'Resolution', 'Keywords', 'Attachment'];
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `orka-lessons-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

async function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this validation lesson? This cannot be undone.')) return;
    try {
        const response = await fetch(`/entries/${id}`, { method: 'DELETE' });
        if (response.ok) {
            selectedId = null;
            await loadEntries();
        }
    } catch (error) {
        console.error('Error deleting entry:', error);
        alert('Failed to delete entry.');
    }
}

function editEntry(id) {
    const entry = allEntries.find(e => String(e.id) === String(id));
    if (!entry) return;
    editingId = String(id);
    modalTitle.textContent = 'Edit Validation Lesson';
    fillForm(entry);
    openModal();
}

function openModal() {
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

addBtn.addEventListener('click', () => {
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
});

function normalizeKeywords(keywords) {
    return Array.isArray(keywords) ? keywords.join(', ') : (keywords || '');
}

function fillForm(data) {
    const today = new Date().toISOString().split('T')[0];
    const fields = {
        project_name: data.project_name || '',
        consultant: data.consultant || '',
        equipment_system: data.equipment_system || '',
        model_number: data.model_number || '',
        validation_phase: data.validation_phase || 'URS',
        intended_outcome: data.intended_outcome || '',
        obstacle: data.obstacle || '',
        resolution: data.resolution || '',
        date_logged: data.date_logged || today,
        attachments: data.attachments || '',
        keywords: normalizeKeywords(data.keywords),
    };
    Object.entries(fields).forEach(([id, value]) => {
        document.getElementById(id).value = value;
    });
}

function getFormData() {
    return {
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
        keywords: document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(Boolean),
    };
}

form.addEventListener('input', () => {
    if (editingId) return;
    const draft = getFormData();
    draft.keywords = document.getElementById('keywords').value;
    localStorage.setItem('lesson_draft', JSON.stringify(draft));
});

closeBtn.addEventListener('click', () => {
    if (!editingId && formHasContent() && !confirm('You have unsaved changes. Close anyway?')) return;
    closeModal();
});

function formHasContent() {
    return ['project_name', 'consultant', 'equipment_system', 'intended_outcome', 'obstacle', 'resolution']
        .some(id => document.getElementById(id).value.trim() !== '');
}

modal.addEventListener('click', (e) => {
    if (e.target === modal) {
        if (!editingId && formHasContent() && !confirm('You have unsaved changes. Close anyway?')) return;
        closeModal();
    }
});

form.addEventListener('submit', async (e) => {
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
            const saved = await response.json().catch(() => null);
            form.reset();
            localStorage.removeItem('lesson_draft');
            closeModal();
            selectedId = editingId || (saved?.id ? String(saved.id) : null);
            editingId = null;
            await loadEntries();
        }
    } catch (error) {
        console.error('Error submitting entry:', error);
        alert('Failed to save entry. Check console for details.');
    }
});

filterTags.forEach(tag => {
    tag.addEventListener('click', () => {
        const filter = tag.getAttribute('data-filter');
        if (activeFilter === filter) {
            activeFilter = null;
            tag.classList.remove('active');
        } else {
            activeFilter = filter;
            filterTags.forEach(t => t.classList.remove('active'));
            tag.classList.add('active');
        }
        activeKeyword = null;
        applyFilters();
        updateURL();
    });
});

function filterChanged(fn) {
    return () => {
        fn();
        applyFilters();
        updateURL();
    };
}

consultantFilter.addEventListener('change', filterChanged(() => { activeConsultant = consultantFilter.value; }));
sortSelect.addEventListener('change', filterChanged(() => { sortOrder = sortSelect.value; }));
dateFromInput.addEventListener('change', filterChanged(() => { dateFrom = dateFromInput.value || null; }));
dateToInput.addEventListener('change', filterChanged(() => { dateTo = dateToInput.value || null; }));
searchInput.addEventListener('input', filterChanged(() => { activeKeyword = null; }));
exportBtn.addEventListener('click', exportCSV);

loadEntries();
