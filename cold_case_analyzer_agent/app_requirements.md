# Cold Case Analyzer Agent - Full Stack App Documentation

## 1. Overview

This document outlines the architecture and setup for the Cold Case Analyzer Agent application. It's a full-stack solution designed to assist in analyzing cold cases, leveraging a FastAPI backend and a Nuxt.js frontend.

## 2. Tech Stack

*   **Backend**: Python with FastAPI
*   **Frontend**: JavaScript/TypeScript with Nuxt.js (as a Single Page Application)
*   **Database**: (Specify if any, e.g., PostgreSQL, SQLite) - *To be defined*
*   **Orchestration/Agent Logic**: Single Docker container for both backend (FastAPI) and frontend (Nuxt.js SPA). FastAPI serves the Nuxt.js static files.

## 3. Project Structure

```
cold-case-analysis/
├── cold_case_analyzer_agent/
│   ├── backend/                 # Backend (FastAPI)
│   │   ├── main.py              # entry point for execution in terminal, without frontend or FastAPI
│   │   ├── app.py               # FastAPI application entry point
│   │   ├── config.py            # Application configuration
│   │   ├── requirements.txt     # Python dependencies
│   │   ├── schemas/             # Pydantic schemas for API requests/responses
│   │   ├── subgraphs/           # Business logic modules (e.g., LangGraph components)
│   │   ├── utils/               # Utility functions
│   │   └── prompts/             # Prompts for LLM interactions
│   ├── frontend/                # Frontend (Nuxt.js)
│   │   ├── components/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── store/
│   │   ├── nuxt.config.js
│   │   └── package.json
│   └── app_requirements.md      # This file
└── README.md
```

## 4. Setup and Installation

### Backend (FastAPI)

1.  **Prerequisites**: Python 3.9+
2.  **Clone Repository**: `git clone <repository_url>`
3.  **Navigate to Backend**: `cd cold-case-analysis/cold_case_analyzer_agent/backend`
4.  **Create Virtual Environment**: `python -m venv venv`
5.  **Activate Environment**:
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`
6.  **Install Dependencies**: `pip install -r requirements.txt`
7.  **Environment Variables**: Create a `.env` file based on `blueprint.env` (if provided) or `config.py` specifications.
    *   `OPENAI_API_KEY="your_api_key"`
    *   *(Add other necessary variables)*
8.  **Run Development Server**: `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000` (FastAPI instance is `app` in `backend/app.py`)

### Frontend (Nuxt.js) - *Assuming standard Nuxt setup*

1.  **Prerequisites**: Node.js (LTS version), npm/yarn
2.  **Navigate to Frontend**: `cd cold-case-analysis/cold_case_analyzer_agent/frontend` (Create this directory if it doesn't exist and initialize Nuxt)
3.  **Install Dependencies**: `npm install` (or `yarn install`)
4.  **Environment Variables**: Create a `.env` file for frontend-specific configurations (e.g., API base URL).
    *   `NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api` (Example)
5.  **Run Development Server**: `npm run dev` (or `yarn dev`)

## 5. Backend API (FastAPI)

Refer to `cold_case_analyzer_agent/backend/app.py` for API route definitions and `cold_case_analyzer_agent/backend/schemas/` for request/response models.

### Routing in Single Container Setup

*   FastAPI will handle all API routes, typically prefixed with `/api/v1` (e.g., `/api/v1/analyze_case`).
*   A catch-all route in FastAPI will serve the `index.html` of the Nuxt.js SPA for any non-API routes, allowing Nuxt.js to handle client-side routing.
*   Static assets for the frontend (JS, CSS, images) will also be served by FastAPI from the directory where Nuxt.js builds its output (e.g., `frontend/dist` or `frontend/.output/public`).

### Key Modules:

*   **`app.py`**: Defines API endpoints (located in `cold_case_analyzer_agent/backend/`).
*   **`config.py`**: Handles application settings and environment variables (in `cold_case_analyzer_agent/backend/`).
*   **`subgraphs/`**: Contains core logic for case analysis, likely using LangGraph (in `cold_case_analyzer_agent/backend/`).
*   **`schemas/`**: Pydantic models for data validation and serialization (in `cold_case_analyzer_agent/backend/`).

### Authentication and State Management:

*   Each user will receive an individual password (from a pre-defined list of passwords) that allows them access to the app. This allows the backend to rate limit each user to a maximum of 10 starting requests per 1 minute (any requests after the initial start do not count towards this limit).
*   Based on the state, the API keeps track of where the graph currently is and which state has to be stored and also returned to the user.

### Example API Endpoints (Illustrative):

*   `POST /api/analyze_case`: Submits case data for analysis.
*   `GET /api/cases/{case_id}`: Retrieves analysis results for a specific case.
*   `GET /api/status`: Checks the status of the backend services.

## 6. Frontend (Nuxt.js)

The Nuxt.js frontend will be a Single Page Application (SPA) providing a chat-like interface for interacting with the Cold Case Analyzer Agent.

### Key Directories:

*   **`pages/`**: Defines the application's views and routes.
    *   `index.vue`: Main landing/dashboard page.
    *   `case/`: Directory for case-specific views (e.g., `_id.vue` for viewing a case, `new.vue` for submitting a new case).
*   **`components/`**: Reusable UI components (e.g., forms, display elements).
*   **`layouts/`**: Defines the overall structure of pages (e.g., default layout with header/footer).
*   **`store/` (if using Pinia/Vuex)**: State management.
*   **`composables/` (Nuxt 3+)**: Reusable composition functions (e.g., for API calls).

### API Interaction:

The frontend will use a library like `axios` or the built-in `$fetch` (Nuxt 3) to communicate with the FastAPI backend API endpoints (e.g., `/api/...`).

### Chat Interaction Flow

The user interacts with the application through a series of steps in a chat-like interface:

1.  **Provide Court Decision**:
    *   User uploads or pastes the full text of a court decision.
2.  **Choice of Law (COL) Section Analysis**:
    *   Backend extracts the COL section and sends it to the user.
    *   User evaluates the extracted COL section.
    *   User can provide feedback (e.g., corrections, alternative text) or type "continue".
    *   If feedback is provided, the backend processes it and provides an updated COL section. This step iterates until the user types "continue".
3.  **Theme Classification**:
    *   Once COL section is accepted, the backend classifies themes from the decision and sends them to the user.
    *   User evaluates the classified themes.
    *   User can provide feedback or type "continue".
    *   If feedback is provided, the backend processes it and provides updated themes. This step iterates until the user types "continue".
4.  **Abstract Generation**:
    *   Backend generates an abstract of the case and sends it to the user.
    *   User evaluates the abstract. (Feedback loop can be added if necessary)
5.  **Relevant Facts Extraction**:
    *   Backend extracts relevant facts and sends them to the user.
    *   User evaluates the relevant facts. (Feedback loop can be added if necessary)
6.  **PIL Provisions Identification**:
    *   Backend identifies relevant Private International Law (PIL) provisions and sends them to the user.
    *   User evaluates the PIL provisions. (Feedback loop can be added if necessary)
7.  **Choice of Law Issue Formulation**:
    *   Backend formulates the choice of law issue and sends it to the user.
    *   User evaluates the choice of law issue. (Feedback loop can be added if necessary)
8.  **Court's Position Summary**:
    *   Backend summarizes the court's position on the choice of law and sends it to the user.
    *   User evaluates the court's position. (Feedback loop can be added if necessary)

Throughout the process, the frontend will manage the display of information from the backend and the collection of user input/feedback.

## 7. Deployment

### Single Docker Container Deployment

The application (both FastAPI backend and Nuxt.js frontend) will be deployed as a single Docker container.

1.  **Dockerfile**: A multi-stage `Dockerfile` will be used:
    *   **Stage 1 (Frontend)**: Build the Nuxt.js SPA. This involves installing Node.js, dependencies, and running the Nuxt build command (e.g., `npm run generate` for SSG or `npm run build` for a more traditional SPA build if Nuxt is configured for SPA output). The static assets are then copied to a known location.
    *   **Stage 2 (Backend)**: Set up the Python environment, install FastAPI and other Python dependencies. Copy the backend code. Copy the built Nuxt.js static assets from Stage 1 into a directory that FastAPI can serve (e.g., `static/`).
2.  **FastAPI Configuration**:
    *   FastAPI will be configured to serve the static files from the Nuxt.js build (e.g., using `StaticFiles` middleware).
    *   A catch-all route in FastAPI will serve the main `index.html` of the Nuxt SPA, enabling client-side routing.
3.  **Container Orchestration**: The Docker image can be deployed to various platforms that support Docker containers (e.g., AWS ECS, Google Cloud Run, Azure Container Instances, Kubernetes, or a single VPS with Docker installed).
4.  **`docker-compose.yaml`**: For local development and simpler deployments, a `docker-compose.yaml` can define the service, build context, and port mappings.

This approach simplifies deployment by packaging the entire application into one artifact.

## 8. Data Management

*   Specify how case data, analysis results, and ground truths are stored, accessed, and managed.
*   (Details to be added based on actual implementation, e.g., database schema, file storage locations).

## 9. Agent Logic (LangGraph)

*   The core analysis is performed by an agent, implemented using LangGraph.
*   This involves defining nodes (processing steps) and edges (transitions) to create a graph that processes input data and generates insights.
*   Prompts for LLM interactions are stored in the `cold_case_analyzer_agent/backend/prompts/` directory.
