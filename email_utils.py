import os
from aiosmtplib import SMTP
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

async def send_email(to_email: str, subject: str, body: str):
    try:
        message = EmailMessage()
        message["From"] = SMTP_USERNAME
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        async with SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True) as smtp:
            await smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            await smtp.send_message(message)

        return {"success": True, "message": "Email sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {e}"}
