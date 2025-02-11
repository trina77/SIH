from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()

class FetchExamTimingRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int

@router.post("/fetch-exam-timing")
async def fetch_exam_timing(request: FetchExamTimingRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Validate user details
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

        # Validate user role and auth token
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to fetch exam timing")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Validate if exam_id is associated with the user_id
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
            raise HTTPException(status_code=403, detail="Exam is not associated with the user")

        # Fetch exam timing
        timing_query = text(
            """
            SELECT start_date, start_time, end_date, end_time 
            FROM exam_timings 
            WHERE exam_id = :exam_id
            """
        )
        result = await db.execute(timing_query, {"exam_id": request.exam_id})
        timing = result.fetchone()

        if not timing:
            return {"message": "No timing set for the given exam"}

        start_date, start_time, end_date, end_time = timing

        # Return the exam timing
        return {
            "message": "Exam timing fetched successfully",
            "timing_details": {
                "exam_id": request.exam_id,
                "start_date": str(start_date),
                "start_time": str(start_time),
                "end_date": str(end_date),
                "end_time": str(end_time),
            }
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
