from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_timings import ExamTimings
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SetExamTimingRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int
    start_date: str  # Format: YYYY-MM-DD
    start_time: str  # Format: HH:MM:SS
    end_date: str    # Format: YYYY-MM-DD
    end_time: str    # Format: HH:MM:SS

@router.post("/set-exam-timing")
async def set_exam_timing(request: SetExamTimingRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch admin details
        admin_query = text(
            """
            SELECT role, auth_token, auth_token_expires_at 
            FROM user_accounts 
            WHERE user_id = :user_id
            """
        )
        result = await db.execute(admin_query, {"user_id": request.user_id})
        admin = result.fetchone()

        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")

        role, stored_auth_token, auth_token_expires_at = admin

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Validate admin role and auth token
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to set exam timings")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the provided exam_id is associated with the user_id
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
            raise HTTPException(status_code=404, detail="Exam not found or not associated with the admin")

        # Validate start and end date-time
        start_datetime = datetime.strptime(f"{request.start_date} {request.start_time}", "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(f"{request.end_date} {request.end_time}", "%Y-%m-%d %H:%M:%S")

        if start_datetime >= end_datetime:
            raise HTTPException(status_code=400, detail="Start date and time must be before end date and time")

        # Check if an entry already exists for the exam_id
        timing_query = text(
            """
            SELECT * 
            FROM exam_timings 
            WHERE exam_id = :exam_id
            """
        )
        result = await db.execute(timing_query, {"exam_id": request.exam_id})
        existing_timing = result.fetchone()

        if existing_timing:
            # Update existing timing
            update_query = text(
                """
                UPDATE exam_timings 
                SET start_date = :start_date, start_time = :start_time, 
                    end_date = :end_date, end_time = :end_time
                WHERE exam_id = :exam_id
                """
            )
            await db.execute(
                update_query,
                {
                    "start_date": request.start_date,
                    "start_time": request.start_time,
                    "end_date": request.end_date,
                    "end_time": request.end_time,
                    "exam_id": request.exam_id,
                },
            )
            await db.commit()

            return {
                "message": "Exam timing updated successfully",
                "timing_details": {
                    "exam_id": request.exam_id,
                    "start_date": request.start_date,
                    "start_time": request.start_time,
                    "end_date": request.end_date,
                    "end_time": request.end_time,
                },
            }
        else:
            # Insert new timing
            new_timing = ExamTimings(
                exam_id=request.exam_id,
                start_date=request.start_date,
                start_time=request.start_time,
                end_date=request.end_date,
                end_time=request.end_time,
            )
            db.add(new_timing)
            await db.commit()
            await db.refresh(new_timing)

            return {
                "message": "Exam timing set successfully",
                "timing_details": {
                    "exam_id": new_timing.exam_id,
                    "start_date": new_timing.start_date,
                    "start_time": new_timing.start_time,
                    "end_date": new_timing.end_date,
                    "end_time": new_timing.end_time,
                },
            }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
