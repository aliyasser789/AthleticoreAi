# app/services/email_service.py

import os
import smtplib
from email.message import EmailMessage


# Read email configuration from environment variables
SMTP_HOST = "smtp-relay.brevo.com"  
SMTP_PORT = 587       # default TLS port
SMTP_USER = "9c176f001@smtp-brevo.com"    # <-- replace
SMTP_PASS = "zBqN8hbaw7Ym2MWH"   # <-- replace
FROM_EMAIL = "ahmadmizo9@gmail.com"   # <-- the sender you verified

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends a plain text email using SMTP.
    Returns True if the email was sent successfully, False otherwise.
    """

    # Ensure credentials exist
    if not SMTP_USER or not SMTP_PASS:
        print("❌ Email not configured correctly (missing SMTP_USER or SMTP_PASS).")
        return False

    # Build the email
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # secure connection
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"📧 Email successfully sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False
