import smtplib
from email.mime.text import MIMEText


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "no-reply@example.com"
    msg["To"] = to_email

    # Example: send via local SMTP server
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)


# @app.post("/notify-user/")
# async def notify_user(email: str, background_tasks: BackgroundTasks):
#     # Schedule the email to be sent in the background
#     background_tasks.add_task(
#         send_email,
#         email,
#         "Welcome!",
#         "Thank you for signing up."
#     )
#     return JSONResponse({"message": f"Email is being sent to {email}"})
