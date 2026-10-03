from sqlalchemy import Column, ForeignKey, Integer, Float, String, Text, DateTime
from config.database import Base
from datetime import datetime


class InterviewResult(Base):
    __tablename__ = "interview_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    candidate_name = Column(String(100))
    total_questions = Column(Integer)
    total_score = Column(Integer)
    average_score = Column(Float)
    recommendation = Column(String(100))
    ats_score = Column(Integer, nullable=True)
    resume_feedback = Column(Text, nullable=True)

    feedback = Column(Text)              # Overall feedback
    question_feedback = Column(Text)     # Question-wise feedback

    created_at = Column(DateTime, default=datetime.utcnow)

    questions = Column(Text)
    answers = Column(Text)
    scores = Column(Text)
    resume_score = Column(Integer)