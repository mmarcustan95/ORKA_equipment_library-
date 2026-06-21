# Orka Consulting Partners - Equipment Knowledge Library

## Overview
The **Equipment Validation Knowledge API** is a lightweight, custom backend designed to capture, centralize, and query institutional knowledge from past equipment validation projects. Built for consultants at Orka Consulting Partners, this tool bridges the gap between complex shop-floor automation systems (like DeltaV and Siemens OpCenter) and accessible, searchable documentation.

This project utilizes a "headless" database architecture, leveraging existing Microsoft 365 infrastructure to ensure zero additional storage costs while maintaining strict corporate security.

## Key Features

### Knowledge Library
*   **Dynamic Knowledge Dashboard:** A modern, responsive interface with a full-width card layout for maximum readability.
*   **Smart Search & Filtering:** Quick-access filters for validation phases (URS, FAT, SAT, IQ, OQ, PQ) and keyword-based search.
*   **Consultant Tracking:** Capture and display the names of experts who logged the lessons.
*   **Draft Persistence:** Entry forms automatically save drafts to local storage, preventing data loss during logging.
*   **Stylized Data Visuals:** Color-coded status boxes for "Obstacles Encountered" (Red) and "Resolutions/Learnings" (Green).
*   **SharePoint Integration:** Direct link to the team's shared file system for quick reference to original documentation.
*   **Premium Aesthetics:** Dark-mode optimized design with smooth transitions, modern typography, and intuitive icons.

### AI Assistant (`/chat`)
*   **Conversational Chat UI:** A Claude-inspired chat interface — AI responses render inline next to a branded avatar with no card boxing, and user messages appear as right-aligned pill bubbles.
*   **Sticky Full-Height Chat Panel:** The chat panel is viewport-height and stays fixed while the upload panel scrolls alongside it.
*   **Markdown Rendering:** AI responses support bullet lists, numbered lists, bold text, inline code, fenced code blocks, and headings.
*   **RAG-Powered Answers:** The assistant searches the embedded knowledge base (ORKA entries + uploaded documents) before falling back to general knowledge.
*   **Document Upload:** Upload PDFs, Word (.docx), or PowerPoint (.pptx) files directly from the sidebar. Documents are chunked, embedded, and immediately available to the AI.
*   **Cited Sources:** Each AI response includes a collapsible sources panel showing which knowledge base entries or uploaded documents were referenced.
*   **Claude-Style Input Bar:** A rounded, focus-highlighted textarea with an arrow send button embedded inside; supports Shift+Enter for multi-line input.
*   **Typing Indicator:** Animated three-dot indicator while the AI is generating a response.

## Architecture & Tech Stack
* **Development Environment:** VS Code
* **Backend Framework:** Python / FastAPI
* **Database (Local Storage):** SQLite (persistent local storage)
* **Vector Search:** Embeddings-based similarity search for AI knowledge retrieval
* **Database Connector:** Supabase Database Hosting service (free tier — 8 GB storage, 500 MB bandwidth/month)
* **Cloud Hosting:** Render (free tier — 500 MB storage, 100 GB bandwidth/month)

## PHASE 2 IMPROVEMENTS
* **Database (Cloud Storage):** Microsoft SharePoint List (target production storage)
* **Database Connector:** Microsoft Graph API
* **Authentication:** Microsoft Entra ID (OAuth2 / Single Tenant for `@orkacp.com` users)
* **Cloud Hosting:** Azure App Service (F1 Free Tier)

## Prerequisites
Before running this project locally, ensure you have the following:
1. **Python 3.9+** installed.
2. **VS Code** configured for Python development.
3. An active **Microsoft Entra ID App Registration** with:
   * A generated Client Secret.
   * `Sites.ReadWrite.All` Application/Delegated permissions for the Microsoft Graph API.
   * A Redirect URI set to `http://localhost:8000/docs/oauth2-redirect`.
4. A populated **SharePoint List** with the standardized validation columns (Project Name, System/Equipment, Validation Phase, Intended Outcome, Obstacle Encountered, Resolution/Learning, Date Logged, Keywords).

## Database Scalability & Limits
Based on the current data structure and average entry size (~7KB per entry), the system is designed to scale efficiently.

### 8GB Storage Estimation
For a database with an 8GB limit (common for lightweight cloud tiers):
*   **Theoretical Maximum:** ~1.2 Million entries.
*   **Realistic Capacity:** ~1,000,000 entries (accounting for SQLite overhead, indexing, and page fragmentation).

*Note: These estimates are based on the inclusion of descriptive validation lessons. If entries are primarily metadata-driven, capacity may increase further.*

## Local Environment Setup

1. **Clone the repository**

## Issues Log
1. Issue when scrolling using the new entry card in tablet/phone mode
