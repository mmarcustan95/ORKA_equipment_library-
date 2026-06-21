const messagesEl = document.getElementById('chat-messages');
const chatForm   = document.getElementById('chat-form');
const chatInput  = document.getElementById('chat-input');
const sendBtn    = document.getElementById('send-btn');
const attachShortcut = document.getElementById('attach-shortcut');

const uploadForm   = document.getElementById('upload-form');
const uploadFile   = document.getElementById('upload-file');
const dropZone     = document.getElementById('drop-zone');
const dropLabel    = document.getElementById('drop-label');
const uploadBtn    = document.getElementById('upload-btn');
const uploadStatus = document.getElementById('upload-status');

let isSubmitting = false;

// Auto-grow textarea up to ~5 lines
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + 'px';
    updateSendState();
});

// Send on Enter, newline on Shift+Enter
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    appendUserBubble(query);
    chatInput.value = '';
    chatInput.style.height = 'auto';
    isSubmitting = true;
    updateSendState();

    const typingEl = appendTypingIndicator();

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        const data = await res.json();
        typingEl.remove();
        appendAiBubble(data.answer, data.sources);
    } catch (err) {
        typingEl.remove();
        appendErrorBubble('Failed to reach the AI. Check that the server is running.');
        console.error(err);
    } finally {
        isSubmitting = false;
        updateSendState();
        chatInput.focus();
    }
});

function appendUserBubble(text) {
    const div = document.createElement('div');
    div.className = 'user-bubble';
    div.innerHTML = `<div class="bubble-body"><p>${escapeHtml(text).replace(/\n/g, '<br>')}</p></div>`;
    messagesEl.appendChild(div);
    scrollToBottom();
}

function appendAiBubble(answer, sources) {
    const div = document.createElement('div');
    div.className = 'ai-bubble';
    const sourcesHtml = buildSourcesHtml(sources);
    div.innerHTML = `
        <div class="bubble-icon">AI</div>
        <div class="bubble-body">
            ${formatAnswer(answer)}
            ${sourcesHtml}
        </div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
}

function appendTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'ai-bubble';
    div.innerHTML = `
        <div class="bubble-icon">AI</div>
        <div class="bubble-body">
            <div class="typing-dots"><span></span><span></span><span></span></div>
        </div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
}

function appendErrorBubble(msg) {
    const div = document.createElement('div');
    div.className = 'ai-bubble error-bubble';
    div.innerHTML = `
        <div class="bubble-icon">!</div>
        <div class="bubble-body"><p>${escapeHtml(msg)}</p></div>
    `;
    messagesEl.appendChild(div);
    scrollToBottom();
}

function buildSourcesHtml(sources) {
    if (!sources || sources.length === 0) return '';

    const entries  = sources.filter(s => s.source_type === 'entry');
    const docs     = sources.filter(s => s.source_type === 'document');

    let html = '<div class="sources-block"><button class="sources-toggle" onclick="toggleSources(this)">📚 Sources (' + sources.length + ')</button><div class="sources-list">';

    if (entries.length > 0) {
        html += `<p class="source-group-label">ORKA Knowledge Base</p>`;
        entries.forEach(s => {
            html += `<div class="source-chip entry-chip">
                <span class="source-type-dot"></span>
                <span class="source-name">${escapeHtml(s.equipment_system)}</span>
                <span class="source-phase">${escapeHtml(s.phase)}</span>
            </div>`;
        });
    }

    if (docs.length > 0) {
        html += `<p class="source-group-label">Uploaded Documents</p>`;
        docs.forEach(s => {
            html += `<div class="source-chip doc-chip">
                <span class="source-type-dot"></span>
                <span class="source-name">${escapeHtml(s.equipment_system)}</span>
            </div>`;
        });
    }

    html += '</div></div>';
    return html;
}

function toggleSources(btn) {
    const list = btn.nextElementSibling;
    const isOpen = list.classList.toggle('open');
    btn.textContent = btn.textContent.replace(isOpen ? '▶' : '▼', isOpen ? '▼' : '▶');
}

function formatAnswer(text) {
    // Extract code blocks first so their content isn't processed as markdown
    const codeBlocks = [];
    let src = text.replace(/```[\w]*\n?([\s\S]*?)```/g, (_, code) => {
        const i = codeBlocks.length;
        codeBlocks.push(escapeHtml(code.trimEnd()));
        return `\x00CODE${i}\x00`;
    });

    // Escape remaining HTML, then restore code blocks as <pre><code>
    src = escapeHtml(src);
    src = src.replace(/\x00CODE(\d+)\x00/g, (_, i) =>
        `<pre><code>${codeBlocks[i]}</code></pre>`
    );

    // Inline formatting
    src = src
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');

    // Process line-by-line for lists and headings
    const lines = src.split('\n');
    let html = '';
    let inUl = false, inOl = false;

    const closeList = () => {
        if (inUl) { html += '</ul>'; inUl = false; }
        if (inOl) { html += '</ol>'; inOl = false; }
    };

    for (const line of lines) {
        const bullet = line.match(/^[-*]\s+(.+)/);
        const num    = line.match(/^\d+\.\s+(.+)/);
        const h3     = line.match(/^###?\s+(.+)/);
        const h2     = line.match(/^##\s+(.+)/);

        if (bullet) {
            if (inOl) { html += '</ol>'; inOl = false; }
            if (!inUl) { html += '<ul>'; inUl = true; }
            html += `<li>${bullet[1]}</li>`;
        } else if (num) {
            if (inUl) { html += '</ul>'; inUl = false; }
            if (!inOl) { html += '<ol>'; inOl = true; }
            html += `<li>${num[1]}</li>`;
        } else {
            closeList();
            if (h3) {
                html += `<h3>${h3[1]}</h3>`;
            } else if (h2) {
                html += `<h4>${h2[1]}</h4>`;
            } else if (line.trim() === '' || line.startsWith('\x00')) {
                html += line;
            } else {
                html += `<p>${line}</p>`;
            }
        }
    }

    closeList();
    return html;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function updateSendState() {
    sendBtn.disabled = isSubmitting || !chatInput.value.trim();
}

attachShortcut.addEventListener('click', () => {
    uploadFile.click();
});

updateSendState();

// ── Upload ────────────────────────────────────────────────────────────────────

uploadFile.addEventListener('change', () => {
    const f = uploadFile.files[0];
    if (f) {
        dropLabel.innerHTML = `<span class="drop-icon">✅</span><span>${escapeHtml(f.name)}</span>`;
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const f = e.dataTransfer.files[0];
    if (f) {
        const dt = new DataTransfer();
        dt.items.add(f);
        uploadFile.files = dt.files;
        dropLabel.innerHTML = `<span class="drop-icon">✅</span><span>${escapeHtml(f.name)}</span>`;
    }
});

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file       = uploadFile.files[0];
    const tag        = document.getElementById('equipment-tag').value.trim();
    const uploadedBy = document.getElementById('uploaded-by').value.trim();

    if (!file || !tag || !uploadedBy) return;

    setUploadStatus('loading', '⏳ Processing document...');
    uploadBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('equipment_tag', tag);
    formData.append('uploaded_by', uploadedBy);

    try {
        const res = await fetch('/documents/upload', { method: 'POST', body: formData });
        const data = await res.json();

        if (!res.ok) {
            setUploadStatus('error', `❌ ${data.detail || 'Upload failed.'}`);
        } else {
            setUploadStatus('success',
                `✅ <strong>${escapeHtml(data.filename)}</strong> ingested — ${data.chunks_stored} chunks stored.`
            );
            uploadForm.reset();
            dropLabel.innerHTML = `<span class="drop-icon">📄</span><span>Click to browse or drag &amp; drop</span>`;
        }
    } catch (err) {
        setUploadStatus('error', '❌ Upload failed. Check that the server is running.');
        console.error(err);
    } finally {
        uploadBtn.disabled = false;
    }
});

function setUploadStatus(type, html) {
    uploadStatus.className = `upload-status upload-status--${type}`;
    uploadStatus.innerHTML = html;
}
