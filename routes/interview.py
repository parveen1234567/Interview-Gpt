from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from services.ai_interviewer import (
    AIResponseError,
    ask_question,
    process_answer,
    generate_report
)
from services.session_auth import get_authenticated_user_id


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/interview"
)


# =========================================================
# START INTERVIEW
# =========================================================

@router.get("/start")
def start_interview(
    request: Request,
    interview_id: str = Query(...),
):
    user_id = get_authenticated_user_id(request)

    try:
        question_data = ask_question(interview_id, user_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "question": question_data["question"],
        "question_number": question_data["question_number"],
    }


# =========================================================
# ANSWER MODEL
# =========================================================

class Answer(BaseModel):

    interview_id: str

    question: str

    answer: str


# =========================================================
# SUBMIT ANSWER
# =========================================================

@router.post("/answer")
def submit_answer(request: Request, data: Answer):
    user_id = get_authenticated_user_id(request)

    # -----------------------------------------------------
    # PROCESS ANSWER
    # -----------------------------------------------------

    try:
        result = process_answer(
            data.interview_id,
            user_id,
            data.question,
            data.answer,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except AIResponseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # =====================================================
    # INTERVIEW COMPLETED
    # =====================================================

    if result["completed"] is True:

        try:
            report = generate_report(data.interview_id, user_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        return {
            "evaluation": result["evaluation"],
            "score": result["score"],
            "next_question": "Interview Completed",
            "completed": True,
            "report": report
        }

    # =====================================================
    # CONTINUE INTERVIEW
    # =====================================================

    return {
        "evaluation": result["evaluation"],
        "score": result["score"],
        "next_question": result["next_question"],
        "completed": False
    }