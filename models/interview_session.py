from sqlalchemy import Column, ForeignKey, Integer, JSON, String, Text

from config.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    candidate_name = Column(String(100), nullable=False)
    resume_score = Column(Integer, nullable=False, default=0)
    ats_score = Column(Integer, nullable=True)
    resume_feedback = Column(Text, nullable=True)
    resume_text = Column(Text, nullable=False)
    initial_questions = Column(JSON, nullable=False)
    current_question_index = Column(Integer, nullable=False, default=0)
    questions_asked = Column(Integer, nullable=False, default=0)
    all_questions = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=False)
    feedback = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="in_progress")
