from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database import get_db
from app.email_utils import send_email
import random
import uuid
from pydantic import BaseModel, EmailStr

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr


class LoginOTPVerificationRequest(BaseModel):
    email: EmailStr
    otp: int


@router.post("/login-request")
async def send_login_otp(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Fetch current time from MySQL
    current_time_query = text("SELECT NOW()")
    result = await db.execute(current_time_query)
    current_time = result.scalar()

    # Check if the email exists in the database and if the account is active
    query = text("SELECT user_id, is_active FROM user_accounts WHERE email = :email")
    result = await db.execute(query, {"email": request.email})
    user = result.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="Email address not found")

    user_id, is_active = user

    # Check if the account is active
    if not is_active:
        raise HTTPException(
            status_code=400,
            detail="Signup is not completed. Please complete signup before attempting login."
        )

    # Generate a new OTP
    otp = random.randint(100000, 999999)

    # Set OTP expiration time (current time + 5 minutes)
    otp_expiration_query = text("SELECT ADDTIME(:current_time, '00:05:00')")
    otp_expiration_result = await db.execute(otp_expiration_query, {"current_time": current_time})
    otp_expires_at = otp_expiration_result.scalar()

    # Update the OTP and expiration time in the database
    update_query = text(
        """
        UPDATE user_accounts
        SET otp = :otp, otp_expires_at = :otp_expires_at
        WHERE user_id = :user_id
        """
    )
    await db.execute(update_query, {"otp": otp, "otp_expires_at": otp_expires_at, "user_id": user_id})
    await db.commit()

    # Send OTP via email
    email_response = await send_email(
        to_email=request.email,
        subject="Your Login OTP",
        body=f"Your OTP is {otp}. It will expire in 5 minutes."
    )
    if not email_response["success"]:
        raise HTTPException(status_code=500, detail=email_response["message"])

    return {"message": "Login OTP sent to your email"}


@router.post("/verify-login-otp")
async def verify_login_otp(request: LoginOTPVerificationRequest, db: AsyncSession = Depends(get_db)):
    # Fetch user details
    query = text(
        """
        SELECT * FROM user_accounts
        WHERE email = :email
        """
    )
    result = await db.execute(query, {"email": request.email})
    user = result.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    (
        user_id,
        first_name,
        last_name,
        email,
        phone_number,
        gender,
        dob,
        role,
        pwd_status,
        pwd_type,
        otp,
        otp_expires_at,
        auth_token,
        auth_token_expires_at,
        is_active
    ) = user

    # Fetch current time from MySQL
    current_time_query = text("SELECT NOW()")
    result = await db.execute(current_time_query)
    current_time = result.scalar()

    # Verify OTP
    if otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_expires_at < current_time:
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Generate a new auth token
    new_auth_token = str(uuid.uuid4())  # Generate 36-character UUID

    # Set auth token expiration (current time + 7 days)
    auth_token_expiration_query = text("SELECT ADDTIME(:current_time, '168:00:00')")
    auth_token_expiration_result = await db.execute(auth_token_expiration_query, {"current_time": current_time})
    new_auth_token_expires_at = auth_token_expiration_result.scalar()

    # Update the auth token and expiration time in the database
    update_query = text(
        """
        UPDATE user_accounts
        SET auth_token = :auth_token, auth_token_expires_at = :auth_token_expires_at, otp = NULL, otp_expires_at = NULL
        WHERE email = :email
        """
    )
    await db.execute(
        update_query,
        {
            "auth_token": new_auth_token,
            "auth_token_expires_at": new_auth_token_expires_at,
            "email": request.email,
        },
    )
    await db.commit()

    # Prepare the response with all user details
    user_data = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone_number": phone_number,
        "gender": gender,
        "dob": str(dob),
        "role": role,
        "pwd_status": pwd_status,
        "pwd_type": pwd_type,
        "auth_token": new_auth_token,
        "auth_token_expires_at": str(new_auth_token_expires_at),
        "is_active": is_active,
        "message": "Login successful"
    }

    return user_data
