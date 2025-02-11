from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exams import Exam
from app.user_accounts_schema import UserAccount
from pydantic import BaseModel, Field
import random
import string

router = APIRouter()


class CreateExamRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_name: str = Field(..., max_length=50)


@router.post("/create-exam")
async def create_exam(request: CreateExamRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch user details
        query = text(
            """
            SELECT role, auth_token, auth_token_expires_at 
            FROM user_accounts 
            WHERE user_id = :user_id
            """
        )
        result = await db.execute(query, {"user_id": request.user_id})
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
            raise HTTPException(status_code=403, detail="User is not authorized to create exams")

        # Check if the provided auth token matches and is not expired
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Generate a unique 6-character alphanumeric exam code
        while True:
            exam_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            code_check_query = text("SELECT exam_id FROM exams WHERE exam_code = :exam_code")
            result = await db.execute(code_check_query, {"exam_code": exam_code})
            if not result.fetchone():
                break  # Exit loop if the code is unique

        # Insert the new exam into the database
        new_exam = Exam(user_id=request.user_id, exam_name=request.exam_name, exam_code=exam_code)
        db.add(new_exam)
        await db.commit()
        await db.refresh(new_exam)

        # Return the new exam details
        return {
            "exam_id": new_exam.exam_id,
            "user_id": new_exam.user_id,
            "exam_name": new_exam.exam_name,
            "exam_code": new_exam.exam_code
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
