from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()

# Request body schema
class VerifyStudentRequest(BaseModel):
    user_id: int
    auth_token: str
    mapping_id: int

@router.post("/verify-student")
async def verify_student(request: VerifyStudentRequest, db: AsyncSession = Depends(get_db)):
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
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to verify students")
        if not is_active:
            raise HTTPException(status_code=403, detail="User account is not active")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the mapping_id is associated with the exam created by the user and verify conditions
        mapping_query = text(
            """
            SELECT mapping_id, exam_id, user_id, admin_verify, student_verify, is_attempted 
            FROM exam_student_mapping 
            WHERE mapping_id = :mapping_id
            """
        )
        result = await db.execute(mapping_query, {"mapping_id": request.mapping_id})
        mapping = result.fetchone()

        if not mapping:
            raise HTTPException(status_code=403, detail="Mapping ID is not found or not associated with the user")

        mapping_id, exam_id, student_user_id, admin_verify, student_verify, is_attempted = mapping

        # Check if admin_verify is False (0), student_verify is True (1), and is_attempted is False
        if admin_verify != 0:
            raise HTTPException(status_code=403, detail="Exam is already verified by admin")
        if student_verify != 1:
            raise HTTPException(status_code=400, detail="Student has not verified the exam yet")
        if is_attempted:
            raise HTTPException(status_code=400, detail="Exam already attempted by student")

        # Update admin_verify to True (1)
        update_query = text(
            """
            UPDATE exam_student_mapping
            SET admin_verify = 1
            WHERE mapping_id = :mapping_id
            """
        )
        await db.execute(update_query, {"mapping_id": request.mapping_id})
        await db.commit()

        # Fetch updated exam details
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

        # Prepare the response with updated data
        updated_data = {
            "mapping_id": mapping_id,
            "exam_id": exam_id,
            "user_id": student_user_id,
            "admin_verify": 1,  # Set to 1 (True)
            "student_verify": student_verify,
            "is_attempted": is_attempted,
        }

        return {
            "message": "Student successfully verified",
            "updated_details": updated_data,
            "exam_name": exam_name,
            "exam_code": exam_code,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
