from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.user_accounts_schema import UserAccount
from app.email_utils import send_email
from pydantic import BaseModel, EmailStr, Field
import random

router = APIRouter()

class SignupRequest(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=10)
    gender: str = Field(..., max_length=1)
    dob: str
    role: str = Field(None, max_length=10)  # Role is now accepted as input
    pwd_status: bool = Field(default=False)  # Add pwd_status to the request
    pwd_type: str = Field(None, max_length=20)  # Add pwd_type to the request

class OTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: int

@router.post("/signup")
async def signup(user: SignupRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Check if a user already exists with the provided email or phone number
        query = text(
            """
            SELECT user_id, otp_expires_at, is_active FROM user_accounts
            WHERE email = :email OR phone_number = :phone_number
            """
        )
        result = await db.execute(query, {"email": user.email, "phone_number": user.phone_number})
        existing_user = result.fetchone()

        if existing_user:
            user_id, otp_expires_at, is_active = existing_user

            # Check if the account is active
            if is_active:
                raise HTTPException(status_code=400, detail="Account already active. Signup cannot proceed.")

            # Check if the existing OTP has expired
            if otp_expires_at and otp_expires_at > current_time:
                raise HTTPException(status_code=400, detail="OTP already sent. Please try again after 5 minutes.")

            # Regenerate OTP and update the database
            new_otp = random.randint(100000, 999999)
            otp_expiration_time_query = text("SELECT ADDTIME(:current_time, '00:05:00')")
            otp_expiration_result = await db.execute(
                otp_expiration_time_query, {"current_time": current_time}
            )
            otp_expires_at = otp_expiration_result.scalar()

            update_query = text(
                """
                UPDATE user_accounts
                SET otp = :otp, otp_expires_at = :otp_expires_at
                WHERE user_id = :user_id
                """
            )
            await db.execute(update_query, {"otp": new_otp, "otp_expires_at": otp_expires_at, "user_id": user_id})
            await db.commit()

            # Send the regenerated OTP via email
            email_response = await send_email(
                to_email=user.email,
                subject="Your OTP for Signup",
                body=f"Your OTP is {new_otp}. It will expire in 5 minutes."
            )
            if not email_response["success"]:
                raise HTTPException(status_code=500, detail=email_response["message"])

            return {"message": "OTP regenerated successfully. Please check your email."}

        # If no existing user, create a new record
        otp_expiration_time_query = text("SELECT ADDTIME(:current_time, '00:05:00')")
        otp_expiration_result = await db.execute(
            otp_expiration_time_query, {"current_time": current_time}
        )
        otp_expires_at = otp_expiration_result.scalar()

        new_otp = random.randint(100000, 999999)
        new_user = UserAccount(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number,
            gender=user.gender,
            dob=user.dob,
            role=user.role,  # Include the role in the new user record
            pwd_status=user.pwd_status,  # Include pwd_status in the new user record
            pwd_type=user.pwd_type,  # Include pwd_type in the new user record
            otp=new_otp,
            otp_expires_at=otp_expires_at,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Send the OTP via email
        email_response = await send_email(
            to_email=user.email,
            subject="Your OTP for Signup",
            body=f"Your OTP is {new_otp}. It will expire in 5 minutes."
        )
        if not email_response["success"]:
            raise HTTPException(status_code=500, detail=email_response["message"])

        return {"message": "Signup initiated. Please check your email for the OTP."}

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Signup failed due to a database error.")


@router.post("/verify-otp")
async def verify_otp(request: OTPVerificationRequest, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch user details
        query = text(
            """
            SELECT otp, otp_expires_at FROM user_accounts
            WHERE email = :email
            """
        )
        result = await db.execute(query, {"email": request.email})
        user = result.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        otp, otp_expires_at = user

        # Fetch current time from MySQL
        current_time_query = text("SELECT NOW()")
        result = await db.execute(current_time_query)
        current_time = result.scalar()

        # Check OTP and expiration
        if otp != request.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        if otp_expires_at < current_time:
            raise HTTPException(status_code=400, detail="OTP has expired")

        # Update OTP fields to NULL and set is_active to TRUE after successful verification
        update_query = text(
            """
            UPDATE user_accounts 
            SET otp = NULL, otp_expires_at = NULL, is_active = TRUE
            WHERE email = :email
            """
        )
        await db.execute(update_query, {"email": request.email})
        await db.commit()

        return {"message": "OTP verified successfully and account activated"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
