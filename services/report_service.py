from config.database import SessionLocal
from models.interview_result import InterviewResult


def save_report(
    user_id,
    total_questions,
    total_score,
    average_score,
    recommendation,
    feedback,
):
    db = SessionLocal()

    report = InterviewResult(
        user_id=user_id,
        total_questions=total_questions,
        total_score=total_score,
        average_score=average_score,
        recommendation=recommendation,
        feedback=feedback,
    )

    db.add(report)
    db.commit()
    db.close()