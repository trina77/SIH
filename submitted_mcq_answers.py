from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.user_accounts_schema import Base  # Use the same Base as UserAccount

class SubmittedMCQAnswers(Base):
    __tablename__ = "submitted_mcq_answers"

    submitted_mcq_answers_id = Column(Integer, primary_key=True, autoincrement=True)
    mcq_id = Column(Integer, ForeignKey("mcq_and_answers.mcq_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.user_id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    submitted_answer = Column(String(1000), nullable=True)

    # Relationships for joins
    mcq = relationship("MCQAndAnswers", back_populates="submitted_answers")
    user = relationship("UserAccount", back_populates="submitted_mcqs")
    exam = relationship("Exam", back_populates="submitted_mcqs")

    def __repr__(self):
        return (
            f"<SubmittedMCQAnswers(submitted_mcq_answers_id={self.submitted_mcq_answers_id}, "
            f"mcq_id={self.mcq_id}, user_id={self.user_id}, exam_id={self.exam_id}, "
            f"submitted_answer={self.submitted_answer})>"
        )
