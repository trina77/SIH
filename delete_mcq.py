from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class DeleteMCQRequest(BaseModel):
    user_id: int
    auth_token: str
    mcq_id: int


@router.delete("/delete-mcq")
async def delete_mcq(request: DeleteMCQRequest, db: AsyncSession = Depends(get_db)):
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

        # Validate admin role and auth token
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to delete MCQs")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the mcq_id exists and fetch its details
        mcq_query = text(
            """
            SELECT mcq_id, exam_id, question, correct_ans, alt_a, alt_b, alt_c 
            FROM mcq_and_answers 
            WHERE mcq_id = :mcq_id
            """
        )
        result = await db.execute(mcq_query, {"mcq_id": request.mcq_id})
        mcq = result.fetchone()

        if not mcq:
            raise HTTPException(status_code=404, detail="MCQ not found")

        mcq_id, exam_id, question, correct_ans, alt_a, alt_b, alt_c = mcq

        # Check if the exam_id is associated with the user_id
        exam_query = text(
            """
            SELECT exam_id 
            FROM exams 
            WHERE exam_id = :exam_id AND user_id = :user_id
            """
        )
        result = await db.execute(exam_query, {"exam_id": exam_id, "user_id": request.user_id})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(status_code=403, detail="Exam is not associated with the provided admin")

        # Delete the MCQ
        delete_query = text(
            """
            DELETE FROM mcq_and_answers 
            WHERE mcq_id = :mcq_id
            """
        )
        await db.execute(delete_query, {"mcq_id": request.mcq_id})
        await db.commit()

        # Prepare the response with deleted data
        deleted_data = {
            "mcq_id": mcq_id,
            "exam_id": exam_id,
            "question": question,
            "correct_ans": correct_ans,
            "alt_a": alt_a,
            "alt_b": alt_b,
            "alt_c": alt_c,
        }

        return {"message": "MCQ deleted successfully", "deleted_mcq": deleted_data}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
