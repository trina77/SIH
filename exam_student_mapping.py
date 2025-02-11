from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship
from app.user_accounts_schema import Base  # Use the same Base as UserAccount

class ExamStudentMapping(Base):
    __tablename__ = "exam_student_mapping"

    mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.user_id"), nullable=False)
    admin_verify = Column(Boolean, default=False)
    student_verify = Column(Boolean, default=False)
    is_attempted = Column(Boolean, default=False)

    # Relationships (optional, useful for joins)
    exam = relationship("Exam", back_populates="student_mappings")
    user = relationship("UserAccount", back_populates="exam_mappings")

    def __repr__(self):
        return (
            f"<ExamStudentMapping(mapping_id={self.mapping_id}, exam_id={self.exam_id}, "
            f"user_id={self.user_id}, admin_verify={self.admin_verify}, "
            f"student_verify={self.student_verify}, is_attempted={self.is_attempted})>"
        )
