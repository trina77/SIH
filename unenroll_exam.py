from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_student_mapping import ExamStudentMapping
from pydantic import BaseModel

router = APIRouter()


class UnenrollExamRequest(BaseModel):
    user_id: int
    auth_token: str
    mapping_id: int


@router.post("/unenroll-exam")
async def unenroll_exam(request: UnenrollExamRequest, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=403, detail="User is not authorized to unenroll from exams")
        if not is_active:
            raise HTTPException(status_code=403, detail="User account is not active")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the mapping_id is associated with the user_id and if admin_verify is true and student_verify is false
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

        # Validate the conditions for unenrollment
        if not admin_verify:
            raise HTTPException(status_code=403, detail="Unenrollment not allowed. Admin verification is pending.")
        if student_verify:
            raise HTTPException(status_code=403, detail="Unenrollment not allowed. Student has already verified enrollment.")

        # Delete the row from exam_student_mapping
        delete_query = text(
            """
            DELETE FROM exam_student_mapping 
            WHERE mapping_id = :mapping_id
            """
        )
        await db.execute(delete_query, {"mapping_id": request.mapping_id})
        await db.commit()

        # Prepare the response with deleted data
        deleted_data = {
            "mapping_id": mapping_id,
            "exam_id": exam_id,
            "user_id": user_id,
            "admin_verify": admin_verify,
            "student_verify": student_verify,
            "is_attempted": is_attempted,
        }

        return {"message": "Successfully unenrolled from the exam", "deleted_data": deleted_data}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
