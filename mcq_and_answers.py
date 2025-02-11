from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.user_accounts_schema import Base  # Use the same Base as UserAccount

class MCQAndAnswers(Base):
    __tablename__ = "mcq_and_answers"

    mcq_id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    question = Column(String(1000), default=None)
    correct_ans = Column(String(1000), default=None)
    alt_a = Column(String(1000), default=None)
    alt_b = Column(String(1000), default=None)
    alt_c = Column(String(1000), default=None)

    # Relationship with Exam
    exam = relationship("Exam", back_populates="mcqs")

    # Relationship with SubmittedMCQAnswers
    submitted_answers = relationship("SubmittedMCQAnswers", back_populates="mcq")

    def __repr__(self):
        return (
            f"<MCQAndAnswers(mcq_id={self.mcq_id}, exam_id={self.exam_id}, "
            f"question={self.question}, correct_ans={self.correct_ans})>"
        )
