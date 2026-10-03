from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from config.database import SessionLocal
from models.interview_result import InterviewResult
from services.session_auth import get_authenticated_user_id


from fastapi.responses import FileResponse, RedirectResponse

from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader

import os
import json
import ast
import re
from pathlib import Path


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def parse_list_data(value):
    """
    Convert database text into a Python list.

    Handles:
    1. JSON list
    2. Python list string
    3. newline-separated values
    """

    if not value:
        return []


    # Already a Python list
    if isinstance(value, list):
        return value


    value = str(value).strip()


    if not value:
        return []


    # -----------------------------------------------------
    # Try JSON
    # -----------------------------------------------------

    try:

        data = json.loads(value)

        if isinstance(data, list):

            return data

    except Exception:

        pass


    # -----------------------------------------------------
    # Try Python list format
    #
    # Example:
    # ['Question 1', 'Question 2']
    # -----------------------------------------------------

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            return data

    except Exception:

        pass


    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    return [
        item.strip()
        for item in value.split("\n\n")
        if item.strip()
    ]


# =========================================================
# PARSE SCORES
# =========================================================

def parse_scores(value):

    if not value:
        return []


    if isinstance(value, list):
        return value


    value = str(value).strip()


    # -----------------------------------------------------
    # JSON
    # -----------------------------------------------------

    try:

        data = json.loads(value)

        if isinstance(data, list):

            return [
                float(x)
                for x in data
            ]

    except Exception:

        pass


    # -----------------------------------------------------
    # Python list
    # -----------------------------------------------------

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            return [
                float(x)
                for x in data
            ]

    except Exception:

        pass


    # -----------------------------------------------------
    # Comma separated
    #
    # Example:
    # 7.0,8.0,6.0,9.0
    # -----------------------------------------------------

    parts = re.split(
        r",|\n",
        value
    )


    scores = []


    for part in parts:

        part = part.strip()

        if not part:
            continue

        try:

            scores.append(
                float(part)
            )

        except Exception:

            pass


    return scores


# =========================================================
# ALL REPORTS
# =========================================================

@router.get("/reports")
def get_reports(request: Request, deleted: int = 0):
    user_id = get_authenticated_user_id(request)

    db: Session = SessionLocal()

    try:

        reports = (
            db.query(InterviewResult)
            .filter(InterviewResult.user_id == user_id)
            .order_by(
                InterviewResult.created_at.desc()
            )
            .all()
        )

    finally:

        db.close()


    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "request": request,
            "reports": reports,
            "deleted": bool(deleted),
        }
    )


@router.post("/reports/{report_id}/delete")
def delete_report(report_id: int, request: Request):
    user_id = get_authenticated_user_id(request)
    db: Session = SessionLocal()
    try:
        report = (
            db.query(InterviewResult)
            .filter(
                InterviewResult.id == report_id,
                InterviewResult.user_id == user_id,
            )
            .first()
        )
        if report is None:
            raise HTTPException(status_code=404, detail="Report not found.")
        generated_pdf = Path("reports") / f"report_{report_id}.pdf"
        try:
            generated_pdf.unlink()
        except FileNotFoundError:
            pass
        db.delete(report)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return RedirectResponse(url="/reports?deleted=1", status_code=303)


# =========================================================
# REPORT DETAILS
# =========================================================

@router.get("/reports/{report_id}")
def report_details(
    report_id: int,
    request: Request
):
    user_id = get_authenticated_user_id(request)

    db: Session = SessionLocal()

    try:

        report = (
            db.query(InterviewResult)
            .filter(
                InterviewResult.id == report_id,
                InterviewResult.user_id == user_id,
            )
            .first()
        )

    finally:

        db.close()


    # -----------------------------------------------------
    # REPORT NOT FOUND
    # -----------------------------------------------------

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")


    # =====================================================
    # PARSE QUESTIONS
    # =====================================================

    questions = parse_list_data(
        report.questions
    )


    # =====================================================
    # PARSE ANSWERS
    # =====================================================

    answers = parse_list_data(
        report.answers
    )


    # =====================================================
    # PARSE SCORES
    # =====================================================

    scores = parse_scores(
        report.scores
    )


    # =====================================================
    # PARSE FEEDBACK
    # =====================================================

    feedbacks = parse_list_data(
        report.question_feedback
    )


    # =====================================================
    # IMPORTANT FIX FOR OLD FEEDBACK FORMAT
    # =====================================================

    if len(feedbacks) == 1:

        single_feedback = str(
            feedbacks[0]
        )


        # If all feedbacks are stored together
        # as:
        #
        # Question 1: ...
        #
        # Feedback:
        # ...
        #
        # Question 2: ...
        #
        # Feedback:
        # ...
        #
        # split them here.

        if "Question 2:" in single_feedback:

            parts = re.split(
                r"(?=Question\s+\d+\s*:)",
                single_feedback
            )

            feedbacks = [
                part.strip()
                for part in parts
                if part.strip()
            ]


    # =====================================================
    # CLEAN FEEDBACK
    # =====================================================

    cleaned_feedbacks = []


    for feedback in feedbacks:

        feedback = str(
            feedback
        ).strip()


        # Remove accidental list markers

        feedback = re.sub(
            r"^\[\s*['\"]?",
            "",
            feedback
        )


        feedback = re.sub(
            r"['\"]?\s*\]$",
            "",
            feedback
        )


        cleaned_feedbacks.append(
            feedback
        )


    feedbacks = cleaned_feedbacks


    # =====================================================
    # CREATE QUESTION-WISE DATA
    # =====================================================

    question_wise_data = []


    total_items = max(
        len(questions),
        len(answers),
        len(scores),
        len(feedbacks)
    )


    for i in range(total_items):

        # -------------------------------------------------
        # Question
        # -------------------------------------------------

        question = ""

        if i < len(questions):

            question = questions[i]


        # -------------------------------------------------
        # Answer
        # -------------------------------------------------

        answer = ""

        if i < len(answers):

            answer = answers[i]


        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        score = 0

        if i < len(scores):

            score = scores[i]


        # -------------------------------------------------
        # Feedback
        # -------------------------------------------------

        feedback = ""

        if i < len(feedbacks):

            feedback = feedbacks[i]


        # -------------------------------------------------
        # Add row
        # -------------------------------------------------

        question_wise_data.append({

            "number": i + 1,

            "question": str(
                question
            ),

            "answer": str(
                answer
            ),

            "score": score,

            "feedback": str(
                feedback
            )

        })


    # =====================================================
    # RETURN TEMPLATE
    # =====================================================

    return templates.TemplateResponse(

        request=request,

        name="report_details.html",

        context={

            "request": request,

            "report": report,

            "question_wise_data":
                question_wise_data,

        }

    )


# =========================================================
# DOWNLOAD PDF
# =========================================================

@router.get("/reports/{report_id}/pdf")
def download_pdf(report_id: int, request: Request):
    user_id = get_authenticated_user_id(request)

    db = SessionLocal()

    try:

        report = (
            db.query(InterviewResult)
            .filter(
                InterviewResult.id == report_id,
                InterviewResult.user_id == user_id,
            )
            .first()
        )

    finally:

        db.close()


    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")


    env = Environment(
        loader=FileSystemLoader(
            "templates"
        )
    )


    template = env.get_template(
        "report_pdf.html"
    )


    html = template.render(report=report)


    pdf_path = (
        f"reports/report_{report_id}.pdf"
    )


    os.makedirs(
        "reports",
        exist_ok=True
    )


    with open(
        pdf_path,
        "wb"
    ) as pdf_file:

        pisa.CreatePDF(
            html,
            dest=pdf_file
        )


    return FileResponse(

        pdf_path,

        media_type="application/pdf",

        filename=(
            f"Interview_Report_{report_id}.pdf"
        )

    )


# =========================================================
# DASHBOARD
# =========================================================

@router.get("/dashboard")
def dashboard(request: Request):
    user_id = get_authenticated_user_id(request)

    db = SessionLocal()

    try:

        total_interviews = (
            db.query(
                InterviewResult
            )
            .filter(InterviewResult.user_id == user_id)
            .count()
        )


        average_ats_score = (
            db.query(
                func.avg(InterviewResult.ats_score)
            )
            .filter(InterviewResult.user_id == user_id)
            .scalar()
            or 0
        )


        average_interview_score = (
            db.query(
                func.avg(
                    InterviewResult.average_score
                )
            )
            .filter(InterviewResult.user_id == user_id)
            .scalar()
            or 0
        )


        highly_recommended = (
            db.query(
                InterviewResult
            )
            .filter(
                InterviewResult.user_id == user_id,
                InterviewResult.recommendation == "Highly Recommended",
            )
            .count()
        )

    finally:

        db.close()


    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={

            "request": request,

            "total_interviews":
                total_interviews,

            "average_ats_score":
                round(
                    average_ats_score,
                    2
                ),

            "average_interview_score":
                round(
                    average_interview_score,
                    2
                ),

            "highly_recommended":
                highly_recommended

        }

    )