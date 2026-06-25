# ORKA Equipment Knowledge Library - Developer Guide

This guide explains how the ORKA Equipment Knowledge Library works.

It is written for consultants who may not have a software background. The goal is to make the codebase less intimidating by explaining the moving parts in business language first, then gradually introducing the technical details.

## 1. What This Application Does

The application is an internal knowledge library for ORKA Consulting Partners.

It helps consultants:

- Record validation lessons learned from real projects.
- Search those lessons by equipment, project, consultant, validation phase, keyword, or date.
- Upload supporting documents such as PDFs, Word documents, and PowerPoint slides.
- Ask an AI assistant questions about validation, commissioning, equipment issues, and uploaded documents.
- See which knowledge base entries or documents were used as sources for an AI answer.

In plain terms, this is a searchable lessons-learned system with an AI assistant on top.

## 2. Big Picture Architecture

The application has four main layers:

1. Frontend
   - The web pages users click on.
   - Built with plain HTML, CSS, and JavaScript.
   - Files live in `main/public/`.

2. Backend API
   - The Python server that receives requests from the frontend.
   - Built with FastAPI.
   - Main file: `main/app.py`.

3. Database layer
   - The code that reads from and writes to the database.
   - Supports local SQLite for simple development.
   - Uses PostgreSQL/Supabase in production for AI document retrieval.
   - Main file: `main/local_db.py`.

4. AI and document processing layer
   - Converts text into embeddings.
   - Uploads and chunks documents.
   - Searches for relevant knowledge base material.
   - Uses Google Gemini for embeddings and chat answers.
   - Main files: `main/vector_embed.py` and `main/ingest_document.py`.

Simple flow:

```text
User clicks or asks a question
        |
Frontend JavaScript sends request
        |
FastAPI backend receives request
        |
Database and AI logic run
        |
Backend returns JSON response
        |
Frontend updates the page
```

## 3. Folder and File Map

```text
.
|-- README.md
|-- requirements.txt
|-- package.json
|-- main/
    |-- app.py
    |-- local_db.py
    |-- models.py
    |-- vector_embed.py
    |-- ingest_document.py
    |-- seed_test_data.py
    |-- config.py
    |-- public/
        |-- landing.html
        |-- index.html
        |-- chat.html
        |-- script.js
        |-- chat.js
        |-- upload.js
        |-- style.css
        |-- favicon.png
```

What each file is for:

- `main/app.py`
  - Starts the FastAPI app.
  - Defines all website routes and API endpoints.
  - Handles chat requests and document uploads.

- `main/local_db.py`
  - Handles database connections.
  - Creates and updates entries.
  - Searches lesson entries and uploaded document chunks.

- `main/models.py`
  - Defines the shape of data used by the app.
  - Example: what fields a validation lesson must have.

- `main/vector_embed.py`
  - Converts normal text into AI search vectors called embeddings.
  - Uses Gemini embedding model.

- `main/ingest_document.py`
  - Extracts text from PDF, Word, and PowerPoint files.
  - Splits document text into chunks.
  - Embeds each chunk.
  - Stores chunks in the database.

- `main/seed_test_data.py`
  - Adds sample validation entries to Supabase for testing.

- `main/config.py`
  - Currently commented out.
  - Looks like earlier Microsoft Graph or SharePoint configuration work.
  - Not active in the current running app.

- `main/public/landing.html`
  - Homepage.

- `main/public/index.html`
  - Main knowledge library page.
  - Shows entries, filters, details, and document upload panel.

- `main/public/chat.html`
  - AI assistant page.

- `main/public/script.js`
  - Browser logic for the knowledge library page.

- `main/public/chat.js`
  - Browser logic for the AI assistant chat page.

- `main/public/upload.js`
  - Browser logic for uploading documents.

- `main/public/style.css`
  - Visual styling for all pages.

## 4. Key Concepts in Plain English

### Frontend

The frontend is what users see in the browser.

In this project, the frontend is not React, Next.js, or another large framework. It is plain HTML, CSS, and JavaScript. That makes it relatively easy to follow:

- HTML decides what exists on the page.
- CSS decides how it looks.
- JavaScript decides what happens when users click, type, search, submit forms, or upload files.

### Backend

The backend is the Python server.

It receives requests such as:

- "Give me all entries."
- "Create this new lesson."
- "Delete this lesson."
- "Upload this document."
- "Ask the AI this question."

The backend sends responses back to the browser in JSON format.

### API Endpoint

An API endpoint is a specific URL that performs an action.

Examples:

- `GET /entries`
  - Fetch all validation lessons.

- `POST /entries`
  - Create a new validation lesson.

- `PUT /entries/{entry_id}`
  - Update an existing validation lesson.

- `DELETE /entries/{entry_id}`
  - Delete a validation lesson.

- `POST /documents/upload`
  - Upload and process documents.

- `POST /chat`
  - Ask the AI assistant a question.

### Database

The database stores the knowledge library.

There are two important tables:

1. `entries`
   - Stores structured validation lessons learned.
   - Example: equipment, phase, obstacle, resolution, keywords.

2. `documents`
   - Stores uploaded document chunks.
   - Example: text extracted from slides, PDFs, and Word documents.

### Embeddings

An embedding is a list of numbers that represents the meaning of text.

Example:

- Text: "HEPA filter failed leak test during OQ"
- Embedding: a long list of numbers

Humans read the sentence. The AI search compares the numbers.

This allows the app to find documents that are semantically related, even if the exact same words are not used.

### Vector Search

Vector search means searching by meaning rather than simple keyword matching.

For example, if a consultant asks:

> Why did the cleanroom fail particle count?

Vector search may still find entries that mention:

- ISO 7 classification
- airborne particles
- HEPA filter loading
- pressure differential

even if the exact phrase "cleanroom fail particle count" is not present.

### RAG

RAG stands for Retrieval-Augmented Generation.

In this project, it means:

1. Retrieve relevant ORKA knowledge first.
2. Give that retrieved context to the AI model.
3. Ask the AI to answer using that context.
4. Show citations/sources in the UI.

The AI is not just answering from memory. It is being given ORKA-specific context before it answers.

## 5. How the User Pages Work

### Homepage: `/`

File:

- `main/public/landing.html`

Purpose:

- Introduces the product.
- Links users to the Knowledge Library and AI Assistant.

Backend route:

- `GET /`

Defined in:

- `main/app.py`

### Knowledge Library: `/library`

Files:

- `main/public/index.html`
- `main/public/script.js`
- `main/public/upload.js`
- `main/public/style.css`

Purpose:

- Shows all validation lessons.
- Lets users search, filter, sort, export, create, edit, and delete entries.
- Includes the document upload panel.

Important user actions:

- Search entries.
- Filter by phase.
- Filter by consultant.
- Filter by date.
- Export CSV.
- Add new lesson.
- Edit lesson.
- Delete lesson.
- Upload documents.

Important backend endpoints used:

- `GET /entries`
- `POST /entries`
- `PUT /entries/{entry_id}`
- `DELETE /entries/{entry_id}`
- `POST /documents/upload`

### AI Assistant: `/assistant`

Files:

- `main/public/chat.html`
- `main/public/chat.js`
- `main/public/style.css`

Purpose:

- Lets users ask questions in natural language.
- Displays AI answers.
- Shows source chips for entries and uploaded documents.

Important backend endpoint used:

- `POST /chat`

## 6. Backend File: `main/app.py`

This is the main application file.

It does three big jobs:

1. Serves pages.
2. Provides API endpoints.
3. Coordinates AI chat and document upload behavior.

### Page Routes

These routes return HTML pages:

- `/`
  - Returns `main/public/landing.html`.

- `/library`
  - Returns `main/public/index.html`.

- `/assistant`
  - Returns `main/public/chat.html`.

- `/chat`
  - Also returns `main/public/chat.html` for browser visits.

Important note:

There are two `/chat` routes with different HTTP methods:

- `GET /chat`
  - Opens the chat page in the browser.

- `POST /chat`
  - Sends a question to the AI assistant.

Same URL, different method.

### Entry API

The entry API manages structured lessons learned.

#### `GET /entries`

Used when the library page loads.

It asks the database for every validation lesson and returns them to the browser.

#### `POST /entries`

Used when a user logs a new lesson.

The backend:

1. Saves the lesson in the database.
2. Generates an embedding for the lesson.
3. Stores the embedding so the AI can search it later.

#### `PUT /entries/{entry_id}`

Used when a user edits a lesson.

The backend:

1. Updates the stored lesson.
2. Regenerates its embedding.
3. Saves the updated embedding.

#### `DELETE /entries/{entry_id}`

Used when a user deletes a lesson.

The backend removes the row from the `entries` table.

### Chat API: `POST /chat`

This is the most important AI endpoint.

When a user asks a question, the backend does this:

```text
1. Convert the question into an embedding.
2. Search structured ORKA entries using vector search.
3. Search uploaded documents using vector search.
4. Search uploaded documents again using keyword fallback.
5. Merge the document results.
6. Build a context block containing relevant entries and documents.
7. Send the context plus the user's question to Gemini.
8. Return the AI answer and source list to the frontend.
```

This is the RAG pipeline.

### Why the Keyword Fallback Exists

Some questions contain short but important terms, such as:

- HVAC
- WFI
- IQ
- OQ
- PQ
- SOP

Vector search is powerful, but short acronyms can sometimes be hard to rank correctly.

For that reason, the app now performs a second document search using text matching. For HVAC questions, it also expands the search terms to include:

- HVAC
- heating
- ventilation
- air conditioning
- environmental control
- temperature
- humidity
- pressure

This helps the assistant find uploaded training slides and related cleanroom material more reliably.

### Chat Prompt Behavior

The system prompt tells the AI:

- Treat both ORKA entries and uploaded documents as the ORKA knowledge base.
- Use ORKA context when it is relevant.
- Cite entries by Entry ID.
- Cite uploaded documents by filename.
- If related context exists but does not directly answer the question, say so clearly.
- Only say no ORKA material was found if the context is empty or unrelated.

This avoids misleading responses such as:

> No relevant entries exist from ORKA knowledge base.

when uploaded documents were actually retrieved.

### Upload API: `POST /documents/upload`

Used by the upload panel on the library page.

The backend:

1. Receives one or more uploaded files.
2. Checks file type.
3. Checks file size and batch size.
4. Sends each accepted file to the ingestion pipeline.
5. Returns a summary to the frontend.

Accepted file types:

- `.pdf`
- `.docx`
- `.pptx`

Default upload limits:

- Up to 8 files per batch.
- Up to 15 MB per file.
- Up to 60 MB total per batch.

These values are configurable with environment variables.

## 7. Database File: `main/local_db.py`

This file is the database access layer.

The rest of the app does not directly write SQL everywhere. Instead, it calls methods in `LocalDatabase`.

That keeps database logic mostly in one place.

### Database Mode Selection

The app checks for this environment variable:

- `DATABASE_URL`

If `DATABASE_URL` exists:

- The app uses PostgreSQL/Supabase.

If `DATABASE_URL` does not exist:

- The app uses local SQLite.

Important limitation:

SQLite can support basic local entries, but document upload and vector search require PostgreSQL/Supabase with pgvector support.

### `entries` Table

The `entries` table stores structured lessons learned.

Main columns:

- `id`
- `project_name`
- `equipment_system`
- `model_number`
- `validation_phase`
- `consultant`
- `intended_outcome`
- `obstacle`
- `resolution`
- `date_logged`
- `attachments`
- `keywords`
- `embedding`

The `embedding` column stores the AI-search representation of the entry.

### `documents` Table

The code expects a `documents` table in PostgreSQL/Supabase.

Expected columns include:

- `id`
- `filename`
- `file_type`
- `content_chunk`
- `chunk_index`
- `equipment_tag`
- `embedding`
- `uploaded_by`

The `documents` table is where uploaded files become searchable.

Each document is split into multiple chunks. Each chunk gets its own row.

Example:

```text
ORKA Academy - Introduction to HVAC.pptx
    chunk 0
    chunk 1
    chunk 2
    ...
```

### Vector Search Methods

`search_entries(...)`

- Searches structured lessons by embedding similarity.
- Used by the AI assistant.

`search_documents(...)`

- Searches uploaded document chunks by embedding similarity.
- Used by the AI assistant.

`search_documents_by_terms(...)`

- Searches uploaded documents by text terms.
- Useful for acronyms, filenames, equipment tags, and exact wording.

### Similarity and Distance

The database uses pgvector syntax:

```sql
embedding <=> query_embedding
```

This returns distance.

Important:

- Lower distance means more similar.
- Higher similarity is easier for humans to understand.

The app also calculates:

```sql
1 - distance as similarity
```

That value is passed into the AI prompt as a helpful retrieval signal.

## 8. Data Models: `main/models.py`

This file defines the expected shape of data.

It uses Pydantic, which validates data coming into and out of the backend.

### `ValidationEntry`

Represents one validation lesson.

Required fields include:

- `project_name`
- `equipment_system`
- `validation_phase`
- `consultant`
- `intended_outcome`
- `obstacle`
- `resolution`
- `date_logged`

Optional fields include:

- `model_number`
- `attachments`
- `keywords`

### `ChatRequest`

Represents a message sent to the AI assistant.

It has one field:

- `query`

Example meaning:

```text
The user asked: "Explain what an HVAC system is."
```

### `ChatResponse`

Represents the AI assistant's response.

It includes:

- `answer`
- `sources`

The frontend displays the answer and then shows source chips underneath.

### `ChatSources`

Represents one source used by the assistant.

Fields:

- `source_id`
- `equipment_system`
- `phase`
- `source_type`

`source_type` is either:

- `entry`
- `document`

## 9. Embeddings File: `main/vector_embed.py`

This file connects to Google Gemini to create embeddings.

Current embedding model:

- `gemini-embedding-001`

Current embedding size:

- 768 dimensions

This means each searchable text item becomes a list of 768 numbers.

### `embed_text(text)`

Used when the app needs to embed any normal text.

Examples:

- User chat question.
- Document chunk.

### `VectorEmbedder`

Used for structured validation entries.

It combines important entry fields into one labelled text string before embedding:

- project name
- equipment system
- model number
- validation phase
- consultant
- intended outcome
- obstacle
- resolution
- date logged
- keywords

This makes the entry easier to find later during AI search.

## 10. Document Ingestion: `main/ingest_document.py`

This file turns uploaded documents into searchable database chunks.

### Supported File Types

- PDF
- Word `.docx`
- PowerPoint `.pptx`

### Extraction

Different extractors are used depending on file type:

- PDFs use `pdfplumber`.
- Word files use `python-docx`.
- PowerPoint files use `python-pptx`.

### Chunking

Large documents are split into smaller chunks.

Current settings:

- `CHUNK_SIZE = 2000`
- `CHUNK_OVERLAP = 200`

Meaning:

- Each chunk is around 2,000 characters.
- Adjacent chunks overlap by 200 characters.

The overlap helps avoid losing meaning at chunk boundaries.

Example:

```text
Chunk 0: characters 0 to 2000
Chunk 1: characters 1800 to 3800
Chunk 2: characters 3600 to 5600
```

### Why Chunking Matters

AI retrieval works better with focused chunks than with entire documents.

If a PowerPoint has 80 slides, storing the whole deck as one giant text block makes retrieval messy. Chunking lets the assistant retrieve the most relevant portion.

### Common Document Upload Limitations

The extractor can only read actual text.

It may struggle with:

- Scanned PDFs.
- Image-only slides.
- Diagrams without selectable text.
- Screenshots of text.

If users upload scanned material, the app may say:

```text
No extractable text - scanned or image-only file?
```

To solve that, the document needs OCR before upload.

## 11. Frontend: Knowledge Library Page

Files:

- `main/public/index.html`
- `main/public/script.js`
- `main/public/upload.js`
- `main/public/style.css`

### What `index.html` Does

Defines the structure of the page:

- Navigation bar.
- Search toolbar.
- Phase filters.
- Stats bar.
- Entry list.
- Detail pane.
- Upload panel.
- New/edit lesson modal.

### What `script.js` Does

Controls the lesson library behavior.

Important responsibilities:

- Load all entries from `GET /entries`.
- Render entries in the master list.
- Render selected entry details.
- Search entries in the browser.
- Filter by phase, consultant, keyword, and date.
- Sort entries.
- Export visible entries to CSV.
- Open and close the entry modal.
- Create new entries.
- Edit existing entries.
- Delete entries.
- Preserve unsaved drafts in browser local storage.

### Browser-Side Filtering

The library loads all entries, then filters them in the browser.

That means:

- Filtering feels fast for normal data sizes.
- No new backend request is needed each time the user types in the search box.

Potential future issue:

- If the database grows very large, filtering should move to the backend.

### Draft Saving

When a user starts logging a new lesson, the form saves draft data in local browser storage.

This helps prevent data loss if the modal is closed accidentally.

### CSV Export

The export button creates a CSV file from the currently visible filtered entries.

It does not export every database row blindly. It exports what the current filters show.

## 12. Frontend: Upload Behavior

File:

- `main/public/upload.js`

This file controls the upload panel.

It handles:

- File selection.
- Folder selection.
- Drag and drop.
- File type checks.
- File size checks.
- Upload progress bar.
- Upload status messages.

Frontend limits match backend defaults:

- 8 files per batch.
- 15 MB per file.
- 60 MB per batch.

The browser sends files to:

- `POST /documents/upload`

The backend then extracts text, chunks it, embeds it, and stores it.

## 13. Frontend: AI Assistant Page

Files:

- `main/public/chat.html`
- `main/public/chat.js`

### What `chat.html` Does

Defines the assistant page:

- Header/navigation.
- Message area.
- Text input.
- Attach shortcut.
- Send button.

### What `chat.js` Does

Controls chat behavior:

- Sends user questions to `POST /chat`.
- Displays user messages.
- Displays AI responses.
- Shows typing indicator.
- Renders basic markdown.
- Shows source chips.
- Handles Enter to send and Shift+Enter for a new line.

### Source Chips

The backend returns a `sources` list.

The frontend groups sources into:

- ORKA Knowledge Base
- Uploaded Documents

This helps users understand where the AI answer came from.

## 14. Environment Variables

Environment variables are settings stored outside the code.

They usually live in:

- `main/.env`

Do not commit real secrets to GitHub.

Important variables:

### `DATABASE_URL`

Used to connect to PostgreSQL/Supabase.

If missing, the app falls back to local SQLite.

Required for:

- Supabase production database.
- Document upload storage.
- Vector search.

### `GEMINI_API_KEY`

Used for Gemini embeddings and AI chat.

Alternative supported name:

- `GOOGLE_API_KEY`

At least one must be set.

### Upload and Retrieval Tuning

Optional variables:

- `MAX_UPLOAD_FILES`
- `MAX_UPLOAD_FILE_MB`
- `MAX_UPLOAD_BATCH_MB`
- `MAX_EXTRACTED_CHARS`
- `ENTRY_SEARCH_TOP_K`
- `DOCUMENT_VECTOR_TOP_K`
- `DOCUMENT_KEYWORD_TOP_K`

Plain meaning:

- Upload variables control file limits.
- Search variables control how many candidate sources are retrieved for the AI.

Increasing search values may improve recall, but can make prompts longer and slower.

## 15. Local Development Setup

Typical setup:

```text
1. Open the project in VS Code.
2. Create or activate a Python virtual environment.
3. Install Python requirements.
4. Create main/.env with required environment variables.
5. Run the FastAPI server.
6. Open the browser.
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
uvicorn main.app:app --reload
```

Open:

```text
http://localhost:8000
```

Useful pages:

- `http://localhost:8000/`
- `http://localhost:8000/library`
- `http://localhost:8000/assistant`
- `http://localhost:8000/docs`

The `/docs` page is automatically generated by FastAPI and lets developers test API endpoints from the browser.

## 16. Production Database Notes

The app expects PostgreSQL/Supabase for full AI functionality.

For document search, Supabase needs:

- A `documents` table.
- An `entries` table.
- pgvector support.
- `embedding` columns that support vector search.

The Python code inserts document chunks, but it does not currently create the `documents` table automatically.

That means the production database schema must be prepared separately.

## 17. AI Assistant Retrieval Flow in Detail

When a user asks:

> Explain what an HVAC system is.

The app does this:

1. `chat.js` sends the query to `POST /chat`.
2. `app.py` receives the query.
3. `embed_text(query)` converts the query to a 768-number embedding.
4. `search_entries(...)` searches structured validation lessons.
5. `search_documents(...)` searches uploaded document chunks by semantic similarity.
6. `build_document_search_terms(...)` extracts useful keywords.
7. If the query includes HVAC, extra related terms are added.
8. `search_documents_by_terms(...)` searches filename, equipment tag, and document text.
9. `merge_document_results(...)` combines vector and keyword results.
10. `app.py` builds a context block.
11. Gemini receives the context and the user question.
12. Gemini writes the answer.
13. The backend returns the answer plus sources.
14. `chat.js` displays the answer and source chips.

This is why an uploaded PowerPoint can influence the AI answer.

## 18. Why the HVAC Retrieval Fix Was Needed

Previously, the assistant could retrieve uploaded documents but still say:

```text
No relevant entries exist from ORKA knowledge base.
```

That wording was misleading because uploaded documents are also part of the ORKA knowledge base.

The fix changed two things:

1. Retrieval was improved.
   - The app now uses both vector search and keyword fallback for uploaded documents.

2. The prompt was improved.
   - The AI is now told to treat both entries and uploaded documents as ORKA knowledge base material.
   - It should not say "No relevant entries" when documents were found.

Better behavior:

```text
I found related ORKA knowledge base material in the uploaded HVAC training slides.
The retrieved slides discuss cleanrooms, classification, and environmental control.
They do not directly define HVAC, so I will supplement with general knowledge.
```

That answer is more honest and more useful.

## 19. Test Data

File:

- `main/seed_test_data.py`

This script inserts sample validation lessons into Supabase.

It is useful for:

- Testing the library page.
- Testing filters.
- Testing AI retrieval.
- Demonstrating the app without real project data.

Run from the project root:

```bash
python -m main.seed_test_data
```

Cleanup command shown in the script:

```sql
DELETE FROM entries WHERE keywords::text LIKE '%testing%';
```

Important:

- Only run seed scripts against a database where test data is acceptable.
- Do not seed production with fake data unless the team intentionally wants demo content.

## 20. Common Troubleshooting

### The page says "Failed to load data"

Likely causes:

- The FastAPI server is not running.
- The browser cannot reach `/entries`.
- The backend crashed on startup.
- Database connection failed.

Check:

- Is `uvicorn main.app:app --reload` running?
- Does `http://localhost:8000/docs` open?
- Is `DATABASE_URL` correct?

### New lessons save but AI search does not find them

Likely causes:

- Embedding generation failed.
- `GEMINI_API_KEY` is missing or invalid.
- The `embedding` column was not updated.

Check:

- Backend logs for embedding warnings.
- `.env` contains a valid Gemini key.
- Database row has a non-empty embedding.

### Document upload succeeds but AI does not use it

Likely causes:

- Document text extraction was poor.
- The file was scanned or image-only.
- Chunks were stored but not semantically close to the question.
- The query uses acronyms or wording not present in the document.

Check:

- Supabase `documents` table.
- `content_chunk` values.
- Whether the relevant text is actually present.

Helpful SQL:

```sql
SELECT chunk_index, content_chunk
FROM documents
WHERE filename ILIKE '%HVAC%'
ORDER BY chunk_index;
```

### Uploaded PDF says no extractable text

Likely cause:

- The PDF is scanned.

Fix:

- Run OCR on the PDF before uploading.

### AI gives a general answer instead of an ORKA-specific answer

Likely causes:

- Relevant context was not retrieved.
- The uploaded document does not actually contain the answer.
- The document chunk is too broad or too sparse.
- Search top-k values are too low.

Possible tuning:

- Increase `DOCUMENT_VECTOR_TOP_K`.
- Increase `DOCUMENT_KEYWORD_TOP_K`.
- Re-upload a cleaner source document.
- Add clearer keywords or equipment tags.

### Document upload fails with file size error

Limits:

- 15 MB per file by default.
- 60 MB per batch by default.

Fix:

- Upload fewer files.
- Compress the document.
- Increase environment variable limits if the hosting environment can handle it.

## 21. How to Safely Make Changes

Recommended workflow:

```text
1. Pull latest code from GitHub.
2. Create or confirm a working branch.
3. Make one focused change.
4. Run the app locally.
5. Test the affected page or endpoint.
6. Commit with a clear message.
7. Push to GitHub.
```

Good commit message examples:

- `Improve HVAC document retrieval`
- `Add upload size validation`
- `Fix consultant filter reset`
- `Update assistant fallback prompt`

Avoid vague messages like:

- `fix`
- `changes`
- `update stuff`

## 22. What to Be Careful With

### Do not commit secrets

Never commit:

- Gemini API keys.
- Supabase database passwords.
- Production database URLs.
- Microsoft client secrets.

Secrets belong in `.env` or deployment environment settings.

### Be careful deleting entries

The delete endpoint permanently removes a row.

There is currently no recycle bin or undo.

### Be careful changing embedding models

If you change the embedding model or embedding dimensions, old embeddings may become incompatible.

For example, current embeddings are 768 dimensions.

Changing that may require re-embedding all entries and documents.

### Be careful changing document chunk size

Chunk size affects retrieval quality.

Smaller chunks:

- More precise.
- More rows in database.
- More embedding calls.

Larger chunks:

- Fewer rows.
- Less precise retrieval.
- May mix unrelated slide content together.

## 23. Known Technical Debt

These are areas that may need future cleanup:

### `config.py` is commented out

It appears to be older Microsoft Graph or SharePoint setup.

Options:

- Remove it if no longer needed.
- Revive it if SharePoint integration returns.
- Move notes into documentation if it is only reference material.

### SQLite and PostgreSQL behavior differ

SQLite works for basic local entry storage.

PostgreSQL/Supabase is required for document ingestion and vector search.

This can confuse developers if they expect every feature to work locally without `DATABASE_URL`.

### Database migrations are minimal

`local_db.py` creates and updates the `entries` table, but production schema management is not fully formalized.

Future improvement:

- Add migration scripts.
- Document exact Supabase SQL setup.
- Version database schema changes.

### No automated tests yet

The project currently relies mainly on manual testing.

Future improvement:

- Add backend tests for entries.
- Add backend tests for upload validation.
- Add tests for document search term generation.
- Add a small test for chat prompt construction.

## 24. Suggested Manual Test Checklist

After changing backend code:

- Start the server.
- Open `/docs`.
- Test `GET /entries`.
- Create a new lesson from `/library`.
- Confirm it appears in the list.
- Edit the lesson.
- Delete a test lesson.
- Ask the assistant a question.
- Confirm sources appear under the answer.

After changing upload code:

- Upload a small PDF.
- Upload a small Word document.
- Upload a small PowerPoint.
- Try an unsupported file type.
- Try a file over the size limit.
- Ask the assistant about uploaded content.

After changing frontend code:

- Check desktop layout.
- Check mobile layout.
- Test search.
- Test filters.
- Test modal open/close.
- Test chat send.
- Test upload progress.

## 25. Glossary

### API

A way for the frontend and backend to talk to each other.

### Backend

The server-side code. In this project, it is Python/FastAPI.

### Frontend

The browser-side code. In this project, it is HTML, CSS, and JavaScript.

### JSON

A structured data format used to send information between browser and server.

### Database

Where the application stores entries, document chunks, and embeddings.

### Embedding

A numerical representation of text meaning.

### Vector Search

Searching by meaning using embeddings.

### RAG

Retrieval-Augmented Generation. The AI retrieves relevant knowledge before answering.

### Chunk

A smaller section of a larger uploaded document.

### Endpoint

A backend URL that performs a specific action.

### Environment Variable

A setting stored outside code, often used for secrets or deployment configuration.

### Supabase

The hosted PostgreSQL database platform used for production-style storage and vector search.

### FastAPI

The Python web framework used to build the backend.

### Gemini

The Google AI model family used for embeddings and assistant responses.

## 26. Quick Reference

Run server:

```bash
uvicorn main.app:app --reload
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Main app file:

```text
main/app.py
```

Database layer:

```text
main/local_db.py
```

AI embeddings:

```text
main/vector_embed.py
```

Document ingestion:

```text
main/ingest_document.py
```

Frontend pages:

```text
main/public/
```

API docs:

```text
http://localhost:8000/docs
```

