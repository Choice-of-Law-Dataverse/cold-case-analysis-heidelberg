from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os, time, uuid

from subgraphs.col_extractor import run_col_section_extraction
from subgraphs.themes_classifier import run_theme_classification
from subgraphs.case_analyzer import run_analysis

app = FastAPI()

# --- Authentication & Rate Limiting ---
security = HTTPBasic()
ALLOWED_PASSWORDS = os.getenv("ALLOWED_PASSWORDS", "").split(",")
RATE_LIMIT = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 10     # initiations per window

def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    pwd = credentials.password
    if pwd not in ALLOWED_PASSWORDS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return pwd

def rate_limit(password: str):
    now = time.time()
    times = RATE_LIMIT.setdefault(password, [])
    RATE_LIMIT[password] = [t for t in times if now - t < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT[password]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: max 10 initiations per minute")
    RATE_LIMIT[password].append(now)

# --- Request/Response Models ---
class CaseTextInput(BaseModel):
    text: str

class FeedbackInput(BaseModel):
    session_id: str
    feedback: str | None = None
    action: str  # e.g., 'continue' or specific feedback action

class AnalysisStepOutput(BaseModel):
    session_id: str
    step_name: str
    content: object
    message_to_user: str | None = None

# --- Session State Management ---
sessions: dict[str, dict] = {}

@app.post("/api/v1/initiate_analysis", response_model=AnalysisStepOutput)
def initiate_analysis(
    payload: CaseTextInput,
    credentials: HTTPBasicCredentials = Depends(security)
):
    password = authenticate(credentials)
    rate_limit(password)

    # Initialize state
    state = {
        "full_text": payload.text,
        "col_section": [],
        "col_section_feedback": [],
        "col_section_evaluation": 0,
        "user_approved_col": False,
        "classification": [],
        "theme_feedback": [],
        "theme_evaluation": 0,
        "user_approved_theme": False,
        "abstract": "",
        "abstract_evaluation": 0,
        "relevant_facts": "",
        "relevant_facts_evaluation": 0,
        "pil_provisions": "",
        "pil_provisions_evaluation": 0,
        "col_issue": "",
        "col_issue_evaluation": 0,
        "courts_position": "",
        "courts_position_evaluation": 0
    }

    # First step: extract COL section
    result = run_col_section_extraction(state)
    col = result.get("col_section", [])[ -1 ]

    session_id = uuid.uuid4().hex
    sessions[session_id] = {
        "state": result,
        "current_step": "col_section",
        "step_index": 0,
        "final": None
    }
    return AnalysisStepOutput(
        session_id=session_id,
        step_name="col_section",
        content=col,
        message_to_user="Please review the extracted Choice of Law section."
    )

@app.post("/api/v1/process_feedback", response_model=AnalysisStepOutput)
def process_feedback(
    payload: FeedbackInput,
    credentials: HTTPBasicCredentials = Depends(security)
):
    password = authenticate(credentials)
    session = sessions.get(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    state = session["state"]
    step = session["current_step"]

    # COL feedback loop
    if step == "col_section":
        if payload.action != "continue":
            state["col_section_feedback"].append(payload.feedback or "")
            result = run_col_section_extraction(state)
            sessions[payload.session_id]["state"] = result
            return AnalysisStepOutput(
                session_id=payload.session_id,
                step_name="col_section",
                content=result.get("col_section", [])[ -1 ],
                message_to_user="Updated COL section based on feedback."
            )
        # continue to themes
        session["current_step"] = "themes"
        result = run_theme_classification(state)
        state.update(result)
        sessions[payload.session_id]["state"] = state
        return AnalysisStepOutput(
            session_id=payload.session_id,
            step_name="themes",
            content=result.get("classification", []),
            message_to_user="Please review the classified themes."
        )

    # Theme feedback loop
    if step == "themes":
        if payload.action != "continue":
            state["theme_feedback"].append(payload.feedback or "")
            result = run_theme_classification(state)
            sessions[payload.session_id]["state"] = result
            return AnalysisStepOutput(
                session_id=payload.session_id,
                step_name="themes",
                content=result.get("classification", []),
                message_to_user="Updated themes based on feedback."
            )
        # proceed to full analysis
        session["current_step"] = "analysis"
        final_state = run_analysis(state)
        session["final"] = final_state
        session["step_index"] = 0

    # Post-analysis steps
    if session.get("current_step") == "analysis":
        final = session.get("final", {})
        steps = ["abstract", "relevant_facts", "pil_provisions", "col_issue", "courts_position"]
        idx = session.get("step_index", 0)
        if idx < len(steps):
            key = steps[idx]
            content = final.get(key, "")
            session['step_index'] = idx + 1
            if session['step_index'] >= len(steps):
                session['current_step'] = 'done'
            return AnalysisStepOutput(
                session_id=payload.session_id,
                step_name=key,
                content=content,
                message_to_user=f"Please review the generated {key.replace('_',' ')}."
            )

    raise HTTPException(status_code=400, detail="Invalid step or action")

@app.get("/api/v1/status")
def get_status():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/api/v1/cases/{session_id}")
def get_case(session_id: str, credentials: HTTPBasicCredentials = Depends(security)):
    """Retrieve current state of a session."""
    authenticate(credentials)
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "current_step": session.get("current_step"),
        "step_index": session.get("step_index"),
        "state": session.get("state"),
        "final": session.get("final")
    }

# --- Serve Nuxt.js SPA ---
static_dir = os.getenv('STATIC_FRONTEND_DIR', '/app/static_frontend')
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="spa")
    @app.middleware("http")
    async def catch_all_spa(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and not request.url.path.startswith("/api"):
            return await app.send_static_file("index.html")
        return response