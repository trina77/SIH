from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()


class FetchStudentDataRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int


@router.post("/fetch-student-data")
async def fetch_student_data(request: FetchStudentDataRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Validate admin user details
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
            raise HTTPException(status_code=403, detail="User is not authorized to fetch student data")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Validate if the exam_id is associated with the admin
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

        # Fetch student data associated with the exam_id
        student_query = text(
            """
            SELECT esm.mapping_id, esm.exam_id, esm.user_id, esm.admin_verify, esm.student_verify, esm.is_attempted,
                   ua.email, ua.first_name, ua.last_name
            FROM exam_student_mapping esm
            INNER JOIN user_accounts ua ON esm.user_id = ua.user_id
            WHERE esm.exam_id = :exam_id
            """
        )
        result = await db.execute(student_query, {"exam_id": request.exam_id})
        student_data = result.fetchall()

        if not student_data:
            raise HTTPException(status_code=404, detail="No students found for the provided exam")

        # Prepare the response
        response_data = []
        for row in student_data:
            response_data.append({
                "mapping_id": row.mapping_id,
                "exam_id": row.exam_id,
                "user_id": row.user_id,
                "admin_verify": 1 if row.admin_verify else 0,
                "student_verify": 1 if row.student_verify else 0,
                "is_attempted": 1 if row.is_attempted else 0,
                "email": row.email,
                "first_name": row.first_name,
                "last_name": row.last_name
            })

        return {"message": "Student data fetched successfully", "students": response_data}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
