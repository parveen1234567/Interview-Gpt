from fastapi import APIRouter, UploadFile, File, Request
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import math
import logging

from groq import AuthenticationError, RateLimitError

import shutil
import os

from services.ai_analyzer import (
    analyze_resume,
    generate_questions,
    extract_candidate_name,
    extract_ats_score
)

from services.pdf_reader import extract_text

from services.ai_interviewer import (
    create_interview_session,
)
from services.session_auth import get_authenticated_user_id


router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


def _rate_limit_retry_seconds(error):
    response = getattr(error, "response", None)
    headers = response.headers if response is not None else {}
    retry_after_ms = headers.get("retry-after-ms")
    retry_after = headers.get("retry-after")

    try:
        if retry_after_ms is not None:
            seconds = float(retry_after_ms) / 1000
        elif retry_after is not None:
            seconds = float(retry_after)
        else:
            return 10
    except (TypeError, ValueError):
        return 10

    if not math.isfinite(seconds) or seconds <= 0:
        return 10
    return math.ceil(seconds)


@router.post("/upload")
async def upload_resume(
    request: Request,
    resume: UploadFile = File(...)
):
    user = request.session.get("user")
    if not isinstance(user, dict) or type(user.get("id")) is not int:
        return RedirectResponse(
            url="/login?next=%2Fupload",
            status_code=303,
        )
    user_id = get_authenticated_user_id(request)

    # =====================================================
    # SAVE PDF
    # =====================================================

    file_path = os.path.join(
        UPLOAD_FOLDER,
        resume.filename
    )


    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            resume.file,
            buffer
        )


    # =====================================================
    # EXTRACT RESUME TEXT
    # =====================================================

    resume_text = extract_text(
        file_path
    )


    # =====================================================
    # CANDIDATE NAME
    # =====================================================

    # =====================================================
    # RESUME ANALYSIS
    # =====================================================

    try:
        candidate_name = extract_candidate_name(resume_text)
        analysis = analyze_resume(resume_text)
        questions = generate_questions(resume_text)
    except AuthenticationError:
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "request": request,
                "error": (
                    "The Groq API key is invalid. Set a valid GROQ_API_KEY in "
                    ".env and restart the application."
                ),
            },
            status_code=503,
        )
    except RateLimitError as exc:
        retry_after = _rate_limit_retry_seconds(exc)
        logger.warning(
            "Groq rate limit reached during resume upload; retry after %s seconds.",
            retry_after,
        )
        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "request": request,
                "error": (
                    "The AI service is temporarily rate-limiting requests. "
                    f"Wait at least {retry_after} seconds, then upload your resume "
                    "again. If this keeps happening, wait a minute and check your "
                    "Groq usage limits. No interview was created."
                ),
            },
            status_code=429,
            headers={"Retry-After": str(retry_after)},
        )


    # =====================================================
    # RESUME SCORE
    # =====================================================

    ats_score = extract_ats_score(
        analysis
    )



    # =====================================================
    # CLEAN QUESTIONS
    # =====================================================

    question_list = []


    for line in questions.split("\n"):

        line = line.strip()


        if not line:

            continue


        # Remove markdown headings

        if line.startswith("**"):

            continue


        # Remove numbering

        match = line.split(
            ".",
            1
        )


        if (
            len(match) == 2
            and match[0].strip().isdigit()
        ):

            line = match[1].strip()


        # Remove bullet

        if line.startswith("-"):

            line = line[1:].strip()


        if line:

            question_list.append(
                line
            )


    # =====================================================
    # KEEP EXACTLY 10 INITIAL QUESTIONS
    # =====================================================

    question_list = question_list[:10]

    if len(question_list) != 10:
        raise HTTPException(
            status_code=502,
            detail="The AI generated fewer than 10 initial questions. Please retry the resume upload.",
        )


    interview_id = create_interview_session(
        question_list=question_list,
        candidate_name=candidate_name,
        resume_score=ats_score,
        ats_score=ats_score,
        resume_feedback=analysis,
        resume_text=resume_text,
        user_id=user_id,
    )
    request.session["latest_ats_interview_id"] = interview_id


    # =====================================================
    # START INTERVIEW
    # =====================================================

    return RedirectResponse(

        url=f"/interview?interview_id={interview_id}",

        status_code=303

    )