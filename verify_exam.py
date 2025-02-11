from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_student_mapping import ExamStudentMapping
from app.exams import Exam
from pydantic import BaseModel

router = APIRouter()

class VerifyExamRequest(BaseModel):
    user_id: int
    auth_token: str
    mapping_id: int

@router.post("/verify-exam")
async def verify_exam(request: VerifyExamRequest, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=403, detail="User is not authorized to verify the exam")
        if not is_active:
            raise HTTPException(status_code=403, detail="User account is not active")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the mapping_id is associated with the user_id and verify admin_verify, student_verify, is_attempted
        mapping_query = text(
            """
            SELECT mapping_id, exam_id, user_id, admin_verify, student_verify, is_attempted 
            FROM exam_student_mapping 
            WHERE mapping_id = :mapping_id AND user_id = :user_id
            """
        )
        result = await db.execute(mapping_query, {"mapping_id": request.mapping_id, "user_id": request.user_id})
        mapping = result.fetchone()

        if not mapping:
            raise HTTPException(status_code=403, detail="Mapping ID is not associated with the user")

        mapping_id, exam_id, user_id, admin_verify, student_verify, is_attempted = mapping

        # Validate the conditions for verifying the exam
        if not admin_verify:
            raise HTTPException(status_code=403, detail="Admin verification is pending. Cannot verify exam.")
        if student_verify:
            raise HTTPException(status_code=403, detail="Student has already verified the exam.")
        if is_attempted:
            raise HTTPException(status_code=403, detail="Exam attempt already made. Cannot verify exam.")

        # Update student_verify to true
        update_query = text(
            """
            UPDATE exam_student_mapping 
            SET student_verify = true 
            WHERE mapping_id = :mapping_id
            """
        )
        await db.execute(update_query, {"mapping_id": request.mapping_id})
        await db.commit()

        # Fetch exam details (exam_name, exam_code)
        exam_query = text(
            """
            SELECT exam_name, exam_code 
            FROM exams 
            WHERE exam_id = :exam_id
            """
        )
        result = await db.execute(exam_query, {"exam_id": exam_id})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        exam_name, exam_code = exam

        # Return the success response with updated entry and exam details
        return {
            "message": "Exam successfully verified",
            "updated_details": {
                "mapping_id": mapping_id,
                "exam_id": exam_id,
                "user_id": user_id,
                "admin_verify": admin_verify,
                "student_verify": 1,
                "is_attempted": is_attempted,
            },
            "exam_name": exam_name,
            "exam_code": exam_code,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
