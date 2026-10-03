from config.database import Base, engine
from models.interview_result import InterviewResult
from models.interview_session import InterviewSession
from models.user import User
from models.password_reset_token import PasswordResetToken

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")