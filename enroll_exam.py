from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_student_mapping import ExamStudentMapping
from pydantic import BaseModel

router = APIRouter()


class EnrollExamRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_code: str


@router.post("/enroll-exam")
async def enroll_exam(request: EnrollExamRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch user details
        user_query = text(
            """
            SELECT role, auth_token, auth_token_expires_at, is_active 
            FROM user_accounts 
            WHERE user_id = :user_id
            """
        )
        result = await db.execute(user_query, {"user_id": request.user_id})
        user = result.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role, stored_auth_token, auth_token_expires_at, is_active = user

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Validate user role, active status, and auth token
        if role != "user":
            raise HTTPException(status_code=403, detail="User is not authorized to enroll in exams")
        if not is_active:
            raise HTTPException(status_code=403, detail="User account is not active")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the exam code exists in the exams table
        exam_query = text(
            """
            SELECT exam_id, exam_name, exam_code 
            FROM exams 
            WHERE exam_code = :exam_code
            """
        )
        result = await db.execute(exam_query, {"exam_code": request.exam_code})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        exam_id, exam_name, exam_code = exam

        # Check if the user is already enrolled in the exam
        mapping_check_query = text(
            """
            SELECT mapping_id 
            FROM exam_student_mapping 
            WHERE exam_id = :exam_id AND user_id = :user_id
            """
        )
        result = await db.execute(mapping_check_query, {"exam_id": exam_id, "user_id": request.user_id})
        if result.fetchone():
            raise HTTPException(status_code=400, detail="User is already enrolled in this exam")

        # Create the entry in the exam_student_mapping table
        new_mapping = ExamStudentMapping(
            exam_id=exam_id,
            user_id=request.user_id,
            student_verify=True,
        )
        db.add(new_mapping)
        await db.commit()
        await db.refresh(new_mapping)

        # Return the success response
        return {
            "message": "User successfully enrolled in the exam",
            "enrollment_details": {
                "mapping_id": new_mapping.mapping_id,
                "exam_id": new_mapping.exam_id,
                "exam_name": exam_name,
                "exam_code": exam_code,
                "user_id": new_mapping.user_id,
                "admin_verify": new_mapping.admin_verify,
                "student_verify": new_mapping.student_verify,
                "is_attempted": new_mapping.is_attempted,
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
