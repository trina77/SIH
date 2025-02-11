from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_student_mapping import ExamStudentMapping
from pydantic import BaseModel

router = APIRouter()


class AddStudentRequest(BaseModel):
    admin_id: int
    admin_auth_token: str
    student_id: int
    exam_id: int


@router.post("/add-student")
async def add_student(request: AddStudentRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch admin details
        admin_query = text(
            """
            SELECT role, auth_token, auth_token_expires_at 
            FROM user_accounts 
            WHERE user_id = :admin_id
            """
        )
        result = await db.execute(admin_query, {"admin_id": request.admin_id})
        admin = result.fetchone()

        if not admin:
            raise HTTPException(status_code=404, detail="Admin user not found")

        admin_role, stored_auth_token, auth_token_expires_at = admin

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Validate admin role and auth token
        if admin_role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to add students")
        if request.admin_auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the provided exam_id is associated with the admin_id
        exam_query = text(
            """
            SELECT exam_id 
            FROM exams 
            WHERE exam_id = :exam_id AND user_id = :admin_id
            """
        )
        result = await db.execute(exam_query, {"exam_id": request.exam_id, "admin_id": request.admin_id})
        exam = result.fetchone()

        if not exam:
            raise HTTPException(
                status_code=403, detail="Exam is not associated with the provided admin"
            )

        # Fetch student details
        student_query = text(
            """
            SELECT first_name, last_name, email, role, is_active 
            FROM user_accounts 
            WHERE user_id = :student_id
            """
        )
        result = await db.execute(student_query, {"student_id": request.student_id})
        student = result.fetchone()

        if not student:
            raise HTTPException(status_code=404, detail="Student user not found")

        first_name, last_name, email, student_role, is_active = student

        # Validate student role and active status
        if student_role != "user":
            raise HTTPException(status_code=400, detail="Provided user is not a student")
        if not is_active:
            raise HTTPException(status_code=400, detail="Student account is not active")

        # Check if the mapping already exists
        mapping_check_query = text(
            """
            SELECT mapping_id 
            FROM exam_student_mapping 
            WHERE exam_id = :exam_id AND user_id = :student_id
            """
        )
        result = await db.execute(mapping_check_query, {"exam_id": request.exam_id, "student_id": request.student_id})
        if result.fetchone():
            raise HTTPException(status_code=400, detail="Student is already assigned to this exam")

        # Insert the mapping
        new_mapping = ExamStudentMapping(
            exam_id=request.exam_id,
            user_id=request.student_id,
            admin_verify=True,
        )
        db.add(new_mapping)
        await db.commit()
        await db.refresh(new_mapping)

        # Return the new mapping with student details
        return {
            "message": "Student successfully added to the exam",
            "mapping_details": {
                "mapping_id": new_mapping.mapping_id,
                "exam_id": new_mapping.exam_id,
                "student_id": new_mapping.user_id,
                "admin_verify": int(new_mapping.admin_verify),
                "student_verify": int(new_mapping.student_verify),
                "is_attempted": int(new_mapping.is_attempted),
            },
            "student_details": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
