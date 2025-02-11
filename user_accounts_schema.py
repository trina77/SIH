from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    Numeric,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserAccount(Base):
    __tablename__ = "user_accounts"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone_number = Column(Numeric(10), unique=True, nullable=False)
    gender = Column(String(1), nullable=False)
    dob = Column(Date, nullable=False)
    role = Column(String(10), default=None)
    pwd_status = Column(Boolean, default=False)
    pwd_type = Column(String(20), default=None)
    otp = Column(Numeric(6), default=None)
    otp_expires_at = Column(DateTime, default=None)
    auth_token = Column(String(36), default=None)
    auth_token_expires_at = Column(DateTime, default=None)
    is_active = Column(Boolean, default=False)

    # Relationship with Exams table
    exams = relationship("Exam", back_populates="user")

    # Relationship with ExamStudentMapping
    exam_mappings = relationship("ExamStudentMapping", back_populates="user")

    # Relationship with SubmittedMCQAnswers
    submitted_mcqs = relationship("SubmittedMCQAnswers", back_populates="user")

    def __repr__(self):
        return (
            f"<UserAccount(user_id={self.user_id}, email={self.email}, "
            f"phone_number={self.phone_number}, auth_token={self.auth_token}, is_active={self.is_active})>"
        )
