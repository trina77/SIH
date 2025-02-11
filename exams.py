from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.user_accounts_schema import Base  # Use the same Base as UserAccount

class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_accounts.user_id"), nullable=False)
    exam_name = Column(String(50), nullable=False)
    exam_code = Column(String(6), unique=True, nullable=False)

    # Relationship back to UserAccount
    user = relationship("UserAccount", back_populates="exams")

    # Relationship with ExamTimings
    timings = relationship("ExamTimings", back_populates="exam", uselist=False)

    # Relationship with ExamStudentMapping
    student_mappings = relationship("ExamStudentMapping", back_populates="exam")

    # Relationship with MCQAndAnswers
    mcqs = relationship("MCQAndAnswers", back_populates="exam")

    # Relationship with SubmittedMCQAnswers
    submitted_mcqs = relationship("SubmittedMCQAnswers", back_populates="exam")

    def __repr__(self):
        return f"<Exam(exam_id={self.exam_id}, user_id={self.user_id}, exam_name={self.exam_name}, exam_code={self.exam_code})>"
