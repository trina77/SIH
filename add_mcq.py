from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.mcq_and_answers import MCQAndAnswers
from pydantic import BaseModel

router = APIRouter()


class AddMCQRequest(BaseModel):
    user_id: int
    auth_token: str
    exam_id: int
    question: str
    correct_ans: str
    alt_a: str
    alt_b: str
    alt_c: str


@router.post("/add-mcq")
async def add_mcq(request: AddMCQRequest, db: AsyncSession = Depends(get_db)):
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

        # Validate user role and auth token
        if role != "admin":
            raise HTTPException(status_code=403, detail="User is not authorized to add MCQs")
        if request.auth_token != stored_auth_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        if not auth_token_expires_at or auth_token_expires_at < current_time:
            raise HTTPException(status_code=401, detail="Authentication token has expired")

        # Check if the exam_id is associated with the user_id
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
            raise HTTPException(
                status_code=403, detail="Exam is not associated with the provided admin"
            )

        # Add the MCQ to the mcq_and_answers table
        new_mcq = MCQAndAnswers(
            exam_id=request.exam_id,
            question=request.question,
            correct_ans=request.correct_ans,
            alt_a=request.alt_a,
            alt_b=request.alt_b,
            alt_c=request.alt_c,
        )
        db.add(new_mcq)
        await db.commit()
        await db.refresh(new_mcq)

        # Return the newly added MCQ
        return {
            "message": "MCQ added successfully",
            "mcq_details": {
                "mcq_id": new_mcq.mcq_id,
                "exam_id": new_mcq.exam_id,
                "question": new_mcq.question,
                "correct_ans": new_mcq.correct_ans,
                "alt_a": new_mcq.alt_a,
                "alt_b": new_mcq.alt_b,
                "alt_c": new_mcq.alt_c,
            },
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
