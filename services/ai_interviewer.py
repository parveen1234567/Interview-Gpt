import os
import re
import uuid
import json

from dotenv import load_dotenv
from groq import Groq

from config.database import SessionLocal
from models.interview_result import InterviewResult
from models.interview_session import InterviewSession


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MAX_QUESTIONS = 15
INITIAL_QUESTIONS = 10


class AIResponseError(RuntimeError):
    pass


def create_interview_session(
    question_list,
    candidate_name,
    resume_score,
    ats_score,
    resume_feedback,
    resume_text,
    user_id,
):
    if len(question_list) != INITIAL_QUESTIONS:
        raise ValueError(
            f"An interview requires exactly {INITIAL_QUESTIONS} initial questions."
        )

    interview_id = str(uuid.uuid4())
    db = SessionLocal()

    try:
        session = InterviewSession(
            id=interview_id,
            user_id=user_id,
            candidate_name=candidate_name or "Unknown Candidate",
            resume_score=resume_score or 0,
            ats_score=ats_score,
            resume_feedback=resume_feedback,
            resume_text=resume_text or "",
            initial_questions=question_list or [],
            current_question_index=0,
            questions_asked=0,
            all_questions=[],
            answers=[],
            scores=[],
            feedback=[],
            status="in_progress",
        )
        db.add(session)
        db.commit()
        return interview_id
    finally:
        db.close()


def _get_session(db, interview_id, user_id):
    session = db.query(InterviewSession).filter(
        InterviewSession.id == interview_id,
        InterviewSession.user_id == user_id,
    ).first()
    if session is None:
        raise LookupError("Interview session was not found.")
    return session


def ask_question(interview_id, user_id):
    db = SessionLocal()

    try:
        session = _get_session(db, interview_id, user_id)

        if session.status != "in_progress":
            return {
                "question": "Interview Completed",
                "question_number": session.questions_asked,
            }

        # Return the unanswered question again if the candidate refreshed the page.
        if len(session.all_questions) > len(session.answers):
            return {
                "question": session.all_questions[-1],
                "question_number": session.questions_asked,
            }

        if session.questions_asked >= MAX_QUESTIONS:
            return {
                "question": "Interview Completed",
                "question_number": session.questions_asked,
            }

        if session.current_question_index >= len(session.initial_questions):
            raise ValueError("No question is available for this interview.")

        question = session.initial_questions[session.current_question_index]
        session.current_question_index += 1
        session.questions_asked += 1
        session.all_questions = session.all_questions + [question]
        db.commit()
        return {
            "question": question,
            "question_number": session.questions_asked,
        }
    finally:
        db.close()


def evaluate_answer(question, answer):
    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer based on the question.

Question:
{question}

Candidate Answer:
{answer}

Evaluate based on:

1. Technical correctness
2. Relevance to the question
3. Clarity
4. Depth
5. Problem solving

Return exactly:

Score: X/10

Feedback:
Short and useful feedback.

Return ONLY the score and feedback.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    evaluation = response.choices[0].message.content.strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", evaluation)
    score = float(match.group(1)) if match else 0
    return evaluation, max(0, min(score, 10))


def generate_followup_question(
    session,
    previous_question,
    previous_answer,
    evaluation,
):
    if session.questions_asked >= MAX_QUESTIONS:
        return "Interview Completed"

    prompt = f"""
You are conducting a strict resume-based technical interview.

The candidate's resume is provided below.

RESUME:
{session.resume_text}


PREVIOUS QUESTION:
{previous_question}


CANDIDATE ANSWER:
{previous_answer}


EVALUATION:
{evaluation}


Generate ONE follow-up question.

CRITICAL RULES:

1. The follow-up MUST be related to the candidate's resume.
2. The follow-up MUST be related to the previous question or the candidate's answer.
3. Ask for deeper technical details about skills, technologies, projects, or experience in the resume.
4. DO NOT introduce any technology that is not present in the resume.
5. DO NOT invent a project or work experience.
6. DO NOT change the technical domain.
7. Keep the question specific and technical.
8. Return ONLY ONE question, with no numbering or explanation.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    followup = response.choices[0].message.content.strip()

    if not followup:
        raise AIResponseError(
            "The AI did not return an adaptive question. Please retry your answer."
        )

    return followup


def process_answer(interview_id, user_id, question, answer):
    db = SessionLocal()

    try:
        session = _get_session(db, interview_id, user_id)
        if session.status != "in_progress":
            raise ValueError("This interview has already been completed.")
        if (
            not session.all_questions
            or session.all_questions[-1] != question
            or len(session.all_questions) != len(session.answers) + 1
        ):
            raise ValueError("The submitted question does not match this interview.")

        evaluation, score = evaluate_answer(question, answer)
        session.answers = session.answers + [answer]
        session.scores = session.scores + [score]
        session.feedback = session.feedback + [evaluation]

        if len(session.answers) == MAX_QUESTIONS:
            session.status = "completed"
            db.commit()
            return {
                "evaluation": evaluation,
                "score": score,
                "next_question": "Interview Completed",
                "completed": True,
            }

        if session.current_question_index < len(session.initial_questions):
            next_question = session.initial_questions[
                session.current_question_index
            ]
            session.current_question_index += 1
        else:
            next_question = generate_followup_question(
                session,
                question,
                answer,
                evaluation,
            )

        session.questions_asked += 1
        session.all_questions = session.all_questions + [next_question]

        db.commit()
        return {
            "evaluation": evaluation,
            "score": score,
            "next_question": next_question,
            "completed": False,
        }
    finally:
        db.close()


def get_recommendation(average_score):
    if average_score >= 8:
        return "Highly Recommended"
    if average_score >= 6:
        return "Strong Candidate"
    if average_score >= 4:
        return "Good Candidate"
    return "Needs Improvement"


def generate_report(interview_id, user_id):
    db = SessionLocal()

    try:
        session = _get_session(db, interview_id, user_id)
        if session.status != "completed":
            raise ValueError("The interview is not complete.")
        if (
            len(session.all_questions) != MAX_QUESTIONS
            or len(session.answers) != MAX_QUESTIONS
            or len(session.scores) != MAX_QUESTIONS
            or len(session.feedback) != MAX_QUESTIONS
        ):
            raise ValueError(
                f"The final report requires exactly {MAX_QUESTIONS} complete question records."
            )

        total_score = sum(session.scores)
        average_score = total_score / len(session.scores) if session.scores else 0
        result = InterviewResult(
            user_id=session.user_id,
            candidate_name=session.candidate_name,
            total_questions=len(session.answers),
            total_score=int(total_score),
            average_score=average_score,
            recommendation=get_recommendation(average_score),
            ats_score=session.ats_score,
            resume_feedback=session.resume_feedback,
            feedback="",
            question_feedback=json.dumps(session.feedback, ensure_ascii=False),
            questions=json.dumps(session.all_questions, ensure_ascii=False),
            answers=json.dumps(session.answers, ensure_ascii=False),
            scores=json.dumps(session.scores, ensure_ascii=False),
            resume_score=session.resume_score,
        )
        db.add(result)
        db.commit()
        db.refresh(result)

        return {
            "id": result.id,
            "candidate_name": session.candidate_name,
            "resume_score": session.resume_score,
            "ats_score": session.ats_score,
            "resume_feedback": session.resume_feedback,
            "overall_score": average_score,
            "total_questions": len(session.answers),
        }
    finally:
        db.close()
