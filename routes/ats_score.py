from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from config.database import SessionLocal
from models.interview_result import InterviewResult
from models.interview_session import InterviewSession
from services.resume_feedback import (
    parse_resume_analysis,
    parse_resume_improvements,
)
from services.session_auth import get_authenticated_user_id


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/ats-score")
def resume_ats_score(request: Request):
    user_id = get_authenticated_user_id(request)
    latest_analysis = None
    db = SessionLocal()
    try:
        latest_session_id = request.session.get("latest_ats_interview_id")
        if isinstance(latest_session_id, str):
            latest_analysis = (
                db.query(InterviewSession)
                .filter(
                    InterviewSession.id == latest_session_id,
                    InterviewSession.user_id == user_id,
                )
                .first()
            )

        if latest_analysis is None:
            latest_analysis = (
                db.query(InterviewResult)
                .filter(InterviewResult.user_id == user_id)
                .order_by(InterviewResult.created_at.desc())
                .first()
            )

        if latest_analysis is None:
            return templates.TemplateResponse(
                request=request,
                name="ats_score.html",
                context={
                    "request": request,
                    "analysis": None,
                    "ats_score": None,
                    "resume_improvements": [],
                    "resume_analysis_sections": [],
                },
            )

        resume_feedback = latest_analysis.resume_feedback
        ats_score = latest_analysis.ats_score
        candidate_name = latest_analysis.candidate_name
        source_name = type(latest_analysis).__name__
    finally:
        db.close()

    return templates.TemplateResponse(
        request=request,
        name="ats_score.html",
        context={
            "request": request,
            "analysis": {
                "candidate_name": candidate_name,
                "resume_feedback": resume_feedback,
                "source_name": source_name,
            },
            "ats_score": ats_score,
            "resume_improvements": parse_resume_improvements(resume_feedback),
            "resume_analysis_sections": parse_resume_analysis(
                resume_feedback, ats_score
            ),
        },
    )
