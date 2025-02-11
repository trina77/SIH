from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class FetchMCQAdminRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int


@router.post("/fetch-mcq-admin")
async def fetch_mcq_admin(request: FetchMCQAdminRequest, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=403, detail="User is not authorized to fetch MCQs")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the exam is associated with the admin
        exam_query = text(
            """
            SELECT exam_id 
            FROM exams 
            WHERE exam_id = :exam_id AND user_id = :user_id
            """
        )
        result = await db.execute(exam_query, {"exam_id": request.exam_id, "user_id": request.user_id})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(status_code=403, detail="Exam is not associated with the provided admin")

        # Fetch all MCQs associated with the exam_id
        mcq_query = text(
            """
            SELECT mcq_id, exam_id, question, correct_ans, alt_a, alt_b, alt_c 
            FROM mcq_and_answers 
            WHERE exam_id = :exam_id
            """
        )
        result = await db.execute(mcq_query, {"exam_id": request.exam_id})
        mcqs = result.fetchall()

        if not mcqs:
            raise HTTPException(status_code=404, detail="No MCQs found for the provided exam")

        # Prepare response
        mcq_list = [
            {
                "mcq_id": mcq.mcq_id,
                "exam_id": mcq.exam_id,
                "question": mcq.question,
                "correct_ans": mcq.correct_ans,
                "alt_a": mcq.alt_a,
                "alt_b": mcq.alt_b,
                "alt_c": mcq.alt_c,
            }
            for mcq in mcqs
        ]

        return {
            "message": "MCQs fetched successfully",
            "mcqs": mcq_list,
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
