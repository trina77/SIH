from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class FetchExamStudentRequest(BaseModel):
    user_id: int
    auth_token: str


@router.post("/fetch-exam-student")
async def fetch_exam_student(request: FetchExamStudentRequest, db: AsyncSession = Depends(get_db)):
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
            raise HTTPException(status_code=403, detail="User is not authorized to fetch exams")
        if not is_active:
            raise HTTPException(status_code=403, detail="User account is not active")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Fetch exams associated with the user_id
        exams_query = text(
            """
            SELECT esm.mapping_id, esm.exam_id, e.exam_name, e.exam_code, esm.admin_verify, esm.student_verify, esm.is_attempted
            FROM exam_student_mapping esm
            JOIN exams e ON esm.exam_id = e.exam_id
            WHERE esm.user_id = :user_id
            """
        )
        result = await db.execute(exams_query, {"user_id": request.user_id})
        exams = result.fetchall()

        if not exams:
            raise HTTPException(status_code=404, detail="No exams found for the user")

        # Prepare the response
        exams_data = [
            {
                "mapping_id": exam.mapping_id,
                "exam_id": exam.exam_id,
                "exam_name": exam.exam_name,
                "exam_code": exam.exam_code,
                "admin_verify": exam.admin_verify,
                "student_verify": exam.student_verify,
                "is_attempted": exam.is_attempted,
            }
            for exam in exams
        ]

        return {"message": "Exams fetched successfully", "exams": exams_data}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
