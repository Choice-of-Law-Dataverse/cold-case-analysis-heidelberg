# Cold Case Analyzer Agent - Full Stack App Documentation

## 1. Overview

This document outlines the architecture and setup for the Cold Case Analyzer Agent application. It's a full-stack solution designed to assist in analyzing cold cases, leveraging a FastAPI backend and a Nuxt.js frontend.

## 2. Tech Stack

*   **Backend**: Python with FastAPI
*   **Frontend**: JavaScript/TypeScript with Nuxt.js
*   **Database**: (Specify if any, e.g., PostgreSQL, SQLite) - *To be defined*
*   **Orchestration/Agent Logic**: LangGraph (as inferred from `cca_langgraph_one_script.py`)

## 3. Project Structure

```
cold-case-analysis/
├── cold_case_analyzer_agent/  # Backend (FastAPI)
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Application configuration
│   ├── requirements.txt       # Python dependencies
│   ├── schemas/               # Pydantic schemas for API requests/responses
│   ├── subgraphs/             # Business logic modules (e.g., LangGraph components)
│   ├── utils/                 # Utility functions
│   ├── prompts/               # Prompts for LLM interactions
│   └── APP_DOCUMENTATION.md   # This file
├── frontend/                  # Frontend (Nuxt.js) - *To be created*
│   ├── components/
│   ├── layouts/
│   ├── pages/
│   ├── store/
│   ├── nuxt.config.js
│   └── package.json
└── README.md
```

## 4. Setup and Installation

### Backend (FastAPI)

1.  **Prerequisites**: Python 3.9+
2.  **Clone Repository**: `git clone <repository_url>`
3.  **Navigate to Backend**: `cd cold-case-analysis/cold_case_analyzer_agent`
4.  **Create Virtual Environment**: `python -m venv venv`
5.  **Activate Environment**:
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`
6.  **Install Dependencies**: `pip install -r requirements.txt`
7.  **Environment Variables**: Create a `.env` file based on `blueprint.env` (if provided) or `config.py` specifications.
    *   `OPENAI_API_KEY="your_api_key"`
    *   *(Add other necessary variables)*
8.  **Run Development Server**: `uvicorn main:app --reload` (or as defined in `main.py`)

### Frontend (Nuxt.js) - *Assuming standard Nuxt setup*

1.  **Prerequisites**: Node.js (LTS version), npm/yarn
2.  **Navigate to Frontend**: `cd cold-case-analysis/frontend` (Create this directory if it doesn't exist)
3.  **Install Dependencies**: `npm install` (or `yarn install`)
4.  **Environment Variables**: Create a `.env` file for frontend-specific configurations (e.g., API base URL).
    *   `NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api` (Example)
5.  **Run Development Server**: `npm run dev` (or `yarn dev`)

## 5. Backend API (FastAPI)

Refer to `cold_case_analyzer_agent/main.py` for API route definitions and `cold_case_analyzer_agent/schemas/` for request/response models.

### Key Modules:

*   **`main.py`**: Defines API endpoints.
*   **`config.py`**: Handles application settings and environment variables.
*   **`subgraphs/`**: Contains core logic for case analysis, likely using LangGraph.
*   **`schemas/`**: Pydantic models for data validation and serialization.

### Example API Endpoints (Illustrative):

*   `POST /api/analyze_case`: Submits case data for analysis.
*   `GET /api/cases/{case_id}`: Retrieves analysis results for a specific case.
*   `GET /api/status`: Checks the status of the backend services.

## 6. Frontend (Nuxt.js)

The Nuxt.js frontend will provide the user interface for interacting with the Cold Case Analyzer Agent.

### Key Directories:

*   **`pages/`**: Defines the application's views and routes.
    *   `index.vue`: Main landing/dashboard page.
    *   `case/`: Directory for case-specific views (e.g., `_id.vue` for viewing a case, `new.vue` for submitting a new case).
*   **`components/`**: Reusable UI components (e.g., forms, display elements).
*   **`layouts/`**: Defines the overall structure of pages (e.g., default layout with header/footer).
*   **`store/` (if using Pinia/Vuex)**: State management.
*   **`composables/` (Nuxt 3+)**: Reusable composition functions (e.g., for API calls).

### API Interaction:

The frontend will use a library like `axios` or the built-in `$fetch` (Nuxt 3) to communicate with the FastAPI backend endpoints. API base URL should be configurable via environment variables.

## 7. Deployment

### Backend (FastAPI)

*   Containerize using Docker.
*   Deploy to a cloud platform (e.g., AWS, Google Cloud, Azure) or a VPS using a production-grade ASGI server like Uvicorn with Gunicorn.

### Frontend (Nuxt.js)

*   **Static Site Generation (SSG)**: `npm run generate`. Deploy the `dist/` (Nuxt 2) or `.output/public/` (Nuxt 3) directory to static hosting (e.g., Netlify, Vercel, GitHub Pages).
*   **Server-Side Rendering (SSR)**: `npm run build`. Deploy the `.output/` (Nuxt 3) or `.nuxt/` and `static/` (Nuxt 2) along with `nuxt.config.js` and `package.json` to a Node.js hosting environment.

## 8. Data Management

*   Specify how case data, analysis results, and ground truths are stored, accessed, and managed.
*   (Details to be added based on actual implementation, e.g., database schema, file storage locations).

## 9. Agent Logic (LangGraph)

*   The core analysis is performed by an agent, likely implemented using LangGraph (see `cca_langgraph_one_script.py` in related directories).
*   This involves defining nodes (processing steps) and edges (transitions) to create a graph that processes input data and generates insights.
*   Prompts for LLM interactions are stored in the `prompts/` directory.
