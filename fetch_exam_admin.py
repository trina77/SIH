from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class FetchExamAdminRequest(BaseModel):
    user_id: int
    auth_token: str


@router.post("/fetch-exam-admin")
async def fetch_exam_admin(request: FetchExamAdminRequest, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=403, detail="User is not authorized to fetch exam details")

        # Check if the provided auth token matches and is not expired
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Fetch exams associated with the user_id
        exams_query = text(
            """
            SELECT exam_id, exam_name, exam_code 
            FROM exams 
            WHERE user_id = :user_id
            """
        )
        result = await db.execute(exams_query, {"user_id": request.user_id})
        exams = result.fetchall()

        if not exams:
            raise HTTPException(status_code=404, detail="No exams found for the given user")

        # Format response
        exams_list = [{"exam_id": exam[0], "exam_name": exam[1], "exam_code": exam[2]} for exam in exams]

        return {
            "user_id": request.user_id,
            "exams": exams_list
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
