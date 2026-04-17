# Orka Consulting Partners - Equipment Knowledge Library

## Overview
The **Equipment Validation Knowledge API** is a lightweight, custom backend designed to capture, centralize, and query institutional knowledge from past equipment validation projects. Built for consultants at Orka Consulting Partners, this tool bridges the gap between complex shop-floor automation systems (like DeltaV and Siemens OpCenter) and accessible, searchable documentation.

This project utilizes a "headless" database architecture, leveraging existing Microsoft 365 infrastructure to ensure zero additional storage costs while maintaining strict corporate security.

## Architecture & Tech Stack
* **Development Environment:** VS Code
* **Backend Framework:** Python / FastAPI
* **Database (Storage):** Microsoft SharePoint List
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

## Local Environment Setup

1. **Clone the repository**
