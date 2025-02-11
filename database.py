from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.user_accounts_schema import Base  # Import Base and UserAccount
from dotenv import load_dotenv
from app.exam_timings import ExamTimings

import os

# Load environment variables
load_dotenv()

# URL-encode the password
password = quote_plus(os.getenv("MYSQL_PASSWORD"))

# MySQL connection URL
DATABASE_URL = f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{password}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"

# Create Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create Session Factory
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get session
async def get_db():
    async with async_session() as session:
        yield session

# Initialize the database (e.g., create tables)
async def init_db():
    # Explicitly import all models to ensure they are registered with Base
    from app.user_accounts_schema import UserAccount
    from app.exams import Exam
    from app.exam_student_mapping import ExamStudentMapping
    from app.mcq_and_answers import MCQAndAnswers
    from app.submitted_mcq_answers import SubmittedMCQAnswers
    from app.exam_timings import ExamTimings

    async with engine.begin() as conn:
        # Create all tables defined in the models
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

# Close the database engine (e.g., for application shutdown)
async def close_db():
    await engine.dispose()
    print("Database connections closed.")
