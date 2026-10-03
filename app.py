import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from routes.auth import router as auth_router
from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.report import router as report_router
from routes.ats_score import router as ats_score_router

from config.database import Base, SessionLocal, engine

# Import models so SQLAlchemy registers the tables
from models.interview_result import InterviewResult
from models.interview_session import InterviewSession
from models.user import User
from models.password_reset_token import PasswordResetToken
from services.resume_feedback import (
    parse_resume_analysis,
    parse_resume_improvements,
)


load_dotenv()
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SESSION_SECRET_KEY:
    raise RuntimeError(
        "SESSION_SECRET_KEY is required. Add a strong random value to .env."
    )


app = FastAPI(title="Interview GPT")


@app.get("/healthz", include_in_schema=False)
def health_check():
    return JSONResponse({"status": "ok"})


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# ROUTERS
# =========================

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(report_router)
app.include_router(ats_score_router)


# =========================
# SESSION MIDDLEWARE
# =========================

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    same_site="lax",
    https_only=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
)


# =========================
# STATIC FILES
# =========================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================
# JINJA2 TEMPLATES
# =========================

templates = Jinja2Templates(
    directory="templates"
)


# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    is_authenticated = isinstance(user, dict) and type(user.get("id")) is int
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "is_authenticated": is_authenticated,
            "user": user if is_authenticated else None,
        }
    )


# =========================
# DASHBOARD
# =========================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    user = request.session.get("user")
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):

        return RedirectResponse(
            "/login",
            status_code=302
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request
        }
    )


# =========================
# UPLOAD PAGE
# =========================

@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    user = request.session.get("user")
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):
        return RedirectResponse(
            "/login?next=%2Fupload",
            status_code=302
        )

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "request": request
        }
    )


# =========================
# INTERVIEW PAGE
# =========================

@app.get("/interview", response_class=HTMLResponse)
async def interview_page(request: Request, interview_id: str = ""):
    user = request.session.get("user")
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):
        return RedirectResponse(
            "/login",
            status_code=302
        )

    ats_score = None
    if interview_id:
        db = SessionLocal()
        try:
            session = db.query(InterviewSession).filter(
                InterviewSession.id == interview_id,
                InterviewSession.user_id == user["id"],
            ).first()
            if session is not None:
                ats_score = session.ats_score
                resume_feedback = session.resume_feedback
            else:
                resume_feedback = None
        finally:
            db.close()
    else:
        resume_feedback = None

    return templates.TemplateResponse(
        request=request,
        name="interview.html",
        context={
            "request": request,
            "ats_score": ats_score,
            "resume_feedback": resume_feedback,
            "resume_improvements": parse_resume_improvements(resume_feedback),
            "resume_analysis_sections": parse_resume_analysis(
                resume_feedback, ats_score
            ),
        }
    )