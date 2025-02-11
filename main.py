import os
from dotenv import load_dotenv  # For loading .env variables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, close_db  # Ensure close_db is implemented
from app.endpoints.signup import router as signup_router
from app.endpoints.login import router as login_router
from app.endpoints.create_exam import router as create_exam_router
from app.endpoints.delete_exam import router as delete_exam_router
from app.endpoints.fetch_exam_admin import router as fetch_exam_admin_router
from app.endpoints.add_student import router as add_student_router
from app.endpoints.remove_student import router as remove_student_router
from app.endpoints.enroll_exam import router as enroll_exam_router
from app.endpoints.fetch_exam_student import router as fetch_exam_student_router
from app.endpoints.unenroll_exam import router as unenroll_exam_router
from app.endpoints.verify_exam import router as verify_exam_router
from app.endpoints.verify_student import router as verify_student_router
from app.endpoints.fetch_student_data import router as fetch_student_data_router
from app.endpoints.add_mcq import router as add_mcq_router
from app.endpoints.fetch_mcq_admin import router as fetch_mcq_admin_router
from app.endpoints.update_mcq import router as update_mcq_router
from app.endpoints.delete_mcq import router as delete_mcq_router
from app.endpoints.set_exam_timing import router as set_exam_timing_router
from app.endpoints.fetch_exam_timing import router as fetch_exam_timing_router
import uvicorn

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    print("Database initialized successfully!")

    try:
        yield  # The application runs while suspended here
    finally:
        # Shutdown code
        await close_db()
        print("Database connections closed.")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application"}

# Include the signup and login routers
app.include_router(signup_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(create_exam_router, prefix="/api")
app.include_router(delete_exam_router, prefix="/api")
app.include_router(fetch_exam_admin_router, prefix="/api")
app.include_router(add_student_router, prefix="/api")
app.include_router(remove_student_router, prefix="/api")
app.include_router(enroll_exam_router, prefix="/api")
app.include_router(fetch_exam_student_router, prefix="/api")
app.include_router(unenroll_exam_router, prefix="/api")
app.include_router(verify_exam_router, prefix="/api")
app.include_router(verify_student_router, prefix="/api")
app.include_router(fetch_student_data_router, prefix="/api")
app.include_router(add_mcq_router, prefix="/api")
app.include_router(fetch_mcq_admin_router, prefix="/api")
app.include_router(update_mcq_router, prefix="/api")
app.include_router(delete_mcq_router, prefix="/api")
app.include_router(set_exam_timing_router, prefix="/api")
app.include_router(fetch_exam_timing_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info")
    )
