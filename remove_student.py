from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.exam_student_mapping import ExamStudentMapping
from pydantic import BaseModel

router = APIRouter()


class RemoveStudentRequest(BaseModel):
    user_id: int
    auth_token: str
    mapping_id: int


@router.post("/remove-student")
async def remove_student(request: RemoveStudentRequest, db: AsyncSession = Depends(get_db)):
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

        admin_role, stored_auth_token, auth_token_expires_at = admin

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Validate admin role and auth token
        if admin_role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to remove students")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the mapping_id is associated with the admin's exam
        mapping_query = text(
            """
            SELECT esm.mapping_id, esm.exam_id, esm.user_id, esm.admin_verify, esm.student_verify, esm.is_attempted 
            FROM exam_student_mapping esm
            JOIN exams e ON esm.exam_id = e.exam_id
            WHERE esm.mapping_id = :mapping_id AND e.user_id = :admin_id
            """
        )
        result = await db.execute(mapping_query, {"mapping_id": request.mapping_id, "admin_id": request.user_id})
        mapping = result.fetchone()

        if not mapping:
            raise HTTPException(
                status_code=403, detail="Mapping ID is not associated with the admin's exams"
            )

        # Delete the row from exam_student_mapping
        delete_query = text(
            """
            DELETE FROM exam_student_mapping 
            WHERE mapping_id = :mapping_id
            """
        )
        await db.execute(delete_query, {"mapping_id": request.mapping_id})
        await db.commit()

        # Prepare the response with deleted data
        deleted_data = {
            "mapping_id": mapping[0],
            "exam_id": mapping[1],
            "student_id": mapping[2],
            "admin_verify": mapping[3],
            "student_verify": mapping[4],
            "is_attempted": mapping[5],
        }

        return {"message": "Student removed successfully", "deleted_data": deleted_data}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
