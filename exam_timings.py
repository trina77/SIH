from sqlalchemy import (
    Column,
    Integer,
    Date,
    Time,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.user_accounts_schema import Base  # Use the same Base as UserAccount

class ExamTimings(Base):
    __tablename__ = "exam_timings"

    timing_id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_date = Column(Date, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationship with Exam
    exam = relationship("Exam", back_populates="timings")

    def __repr__(self):
        return (
            f"<ExamTimings(timing_id={self.timing_id}, exam_id={self.exam_id}, "
            f"start_date={self.start_date}, start_time={self.start_time}, "
            f"end_date={self.end_date}, end_time={self.end_time})>"
        )
