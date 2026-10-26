import asyncio
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _valid_email_address(address: str) -> bool:
    name, parsed_address = parseaddr(address)
    if name or not parsed_address or parsed_address != address or parsed_address.count("@") != 1:
        return False
    local_part, domain = parsed_address.split("@", 1)
    return bool(
        local_part
        and domain
        and not any(character.isspace() for character in parsed_address)
        and "\r" not in parsed_address
        and "\n" not in parsed_address
    )


def _send_email_sync(recipient: str, subject: str, body: str) -> str:
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_email or not sender_password:
        return "Email is not configured. Set SENDER_EMAIL and SENDER_PASSWORD in .env."
    if not _valid_email_address(recipient):
        return "Invalid recipient email address."
    if not subject.strip() or not body.strip():
        return "Email subject and message must not be empty."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.error("Email delivery failed (%s)", type(exc).__name__)
        return f"Email delivery failed ({type(exc).__name__}). Check the account configuration and network."

    return f"Email sent successfully to {recipient}."


async def send_email_now(recipient: str, subject: str, body: str) -> str:
    return await asyncio.to_thread(_send_email_sync, recipient, subject, body)


def _send_sms_sync(phone_number: str, message: str) -> str:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    if not all((account_sid, auth_token, from_number)):
        return "SMS is not configured. Set the Twilio credentials in .env."
    if not phone_number.strip() or not message.strip():
        return "SMS recipient and message must not be empty."

    try:
        from requests.exceptions import RequestException
        from twilio.base.exceptions import TwilioRestException
        from twilio.rest import Client
    except ImportError:
        return "Twilio is not installed. Install the optional twilio package to enable SMS."

    try:
        client = Client(account_sid, auth_token)
        sms = client.messages.create(body=message, from_=from_number, to=phone_number)
    except (OSError, RequestException, TwilioRestException, ValueError) as exc:
        logger.error("SMS delivery failed (%s)", type(exc).__name__)
        return f"SMS delivery failed ({type(exc).__name__}). Check the account configuration and network."

    return f"SMS accepted by Twilio for {phone_number}. Message ID: {sms.sid}."


async def send_sms_now(phone_number: str, message: str) -> str:
    return await asyncio.to_thread(_send_sms_sync, phone_number, message)
