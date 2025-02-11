from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class DeleteExamRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int


@router.delete("/delete-exam")
async def delete_exam(request: DeleteExamRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch user details
        user_query = text(
            """
            SELECT role, auth_token, auth_token_expires_at 
            FROM user_accounts 
            WHERE user_id = :user_id
            """
        )
        result = await db.execute(user_query, {"user_id": request.user_id})
        user = result.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role, stored_auth_token, auth_token_expires_at = user

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Check if the user is an admin
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to delete exams")

        # Check if the provided auth token matches and is not expired
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the exam is associated with the user
        exam_query = text(
            """
            SELECT exam_id FROM exams 
            WHERE exam_id = :exam_id AND user_id = :user_id
            """
        )
        result = await db.execute(exam_query, {"exam_id": request.exam_id, "user_id": request.user_id})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found or not associated with the user")

        # Delete any associated records from the exam_student_mapping table
        delete_mapping_query = text(
            """
            DELETE FROM exam_student_mapping 
            WHERE exam_id = :exam_id
            """
        )
        await db.execute(delete_mapping_query, {"exam_id": request.exam_id})

        # Delete the exam from the exams table
        delete_exam_query = text(
            """
            DELETE FROM exams 
            WHERE exam_id = :exam_id
            """
        )
        await db.execute(delete_exam_query, {"exam_id": request.exam_id})

        await db.commit()

        return {"message": "Exam and associated student mappings deleted successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
