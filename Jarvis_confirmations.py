import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Any

from livekit.agents import RunContext, function_tool

from Jarvis_email import _valid_email_address, send_email_now, send_sms_now
from Jarvis_system_control import perform_system_action

_PENDING_TTL_SECONDS = 120
_lock = threading.Lock()


@dataclass
class _PendingAction:
    action: str
    details: dict[str, str]
    created_sequence: int
    created_at: float


@dataclass
class _SessionConfirmationState:
    transcript: str = ""
    transcript_sequence: int = 0
    pending: _PendingAction | None = None


_states: dict[int, _SessionConfirmationState] = {}

_CONFIRMATION_PHRASES = {
    "email": {"confirm email", "पुष्टि ईमेल भेजो"},
    "sms": {"confirm sms", "पुष्टि एसएमएस भेजो"},
    "shutdown": {"confirm shutdown", "पुष्टि शटडाउन"},
    "restart": {"confirm restart", "पुष्टि रीस्टार्ट"},
    "sleep": {"confirm sleep", "पुष्टि स्लीप"},
    "lock": {"confirm lock", "पुष्टि लॉक"},
    "logout": {"confirm logout", "पुष्टि लॉगआउट"},
}
_SYSTEM_ACTIONS = {"shutdown", "restart", "sleep", "lock", "logout"}


def _normalize_phrase(text: str) -> str:
    return " ".join(
        text.casefold()
        .strip()
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .split()
    )


def _session_key(ctx: RunContext[Any]) -> int:
    return id(ctx.session)


def record_user_transcript(session_key: int, transcript: str, is_final: bool) -> None:
    if not is_final:
        return
    with _lock:
        state = _states.setdefault(session_key, _SessionConfirmationState())
        state.transcript = transcript
        state.transcript_sequence += 1


def clear_session_confirmation_state(session_key: int) -> None:
    with _lock:
        _states.pop(session_key, None)


def _confirmation_error(
    action: str,
    transcript: str,
    transcript_sequence: int,
    pending: _PendingAction,
    now: float,
) -> str | None:
    if now - pending.created_at > _PENDING_TTL_SECONDS:
        return "expired"
    if transcript_sequence <= pending.created_sequence:
        return "missing"
    if _normalize_phrase(transcript) not in _CONFIRMATION_PHRASES[action]:
        return "mismatch"
    return None


def _stage_action(session_key: int, action: str, details: dict[str, str]) -> str:
    now = time.monotonic()
    with _lock:
        state = _states.setdefault(session_key, _SessionConfirmationState())
        if state.pending and now - state.pending.created_at <= _PENDING_TTL_SECONDS:
            return "There is already a pending action. Confirm it or say cancel before requesting another."
        state.pending = _PendingAction(
            action=action,
            details=details,
            created_sequence=state.transcript_sequence,
            created_at=now,
        )
    return _confirmation_prompt(action, details)


def _confirmation_prompt(action: str, details: dict[str, str]) -> str:
    phrase = _confirmation_instruction(action)
    if action == "email":
        summary = (
            f"Email draft for {details['recipient']}. Subject: {details['subject']}. "
            f"Message: {details['body']}."
        )
    elif action == "sms":
        summary = f"SMS draft for {details['phone_number']}: {details['message']}."
    else:
        summary = f"This will {action} this computer."
    return f"{summary} Nothing has been done yet. To proceed, say exactly: {phrase}. To discard it, say cancel."


def _confirmation_instruction(action: str) -> str:
    phrases = sorted(_CONFIRMATION_PHRASES[action])
    if len(phrases) == 1:
        return phrases[0]
    return f"{phrases[0]} (or {phrases[1]})"


@function_tool
async def prepare_email(recipient: str, subject: str, body: str, ctx: RunContext[Any]) -> str:
    """Prepare an email draft and read its recipient, subject, and body aloud. Never sends it.

    Args:
        recipient: Full recipient email address.
        subject: Email subject.
        body: Complete email body.
    """
    details = {
        "recipient": recipient.strip(),
        "subject": subject.strip(),
        "body": body.strip(),
    }
    if not all(details.values()):
        return "The recipient, subject, and message are required. Nothing was sent."
    if not _valid_email_address(details["recipient"]):
        return "That recipient email address is invalid. Nothing was sent."
    if "\r" in details["subject"] or "\n" in details["subject"]:
        return "The email subject cannot contain line breaks. Nothing was sent."
    return _stage_action(_session_key(ctx), "email", details)


@function_tool
async def prepare_sms(phone_number: str, message: str, ctx: RunContext[Any]) -> str:
    """Prepare an SMS draft and read its recipient and message aloud. Never sends it.

    Args:
        phone_number: Full phone number, including country code.
        message: Complete SMS message.
    """
    details = {"phone_number": phone_number.strip(), "message": message.strip()}
    if not all(details.values()):
        return "The phone number and message are required. Nothing was sent."
    return _stage_action(_session_key(ctx), "sms", details)


@function_tool
async def request_system_action(action: str, ctx: RunContext[Any]) -> str:
    """Request a power action. This only asks for confirmation and does not execute it.

    Args:
        action: One of shutdown, restart, sleep, lock, or logout.
    """
    normalized_action = _normalize_phrase(action)
    if normalized_action not in _SYSTEM_ACTIONS:
        return "Unsupported system action. Choose shutdown, restart, sleep, lock, or logout."
    return _stage_action(_session_key(ctx), normalized_action, {})


@function_tool
async def confirm_pending_action(ctx: RunContext[Any]) -> str:
    """Execute a pending email, SMS, or system action only after the user says its exact confirmation phrase."""
    session_key = _session_key(ctx)
    with _lock:
        state = _states.get(session_key)
        if not state or not state.pending:
            return "There is no pending action to confirm."
        pending = state.pending
        error = _confirmation_error(
            pending.action,
            state.transcript,
            state.transcript_sequence,
            pending,
            time.monotonic(),
        )
        if error == "expired":
            state.pending = None
            return "The confirmation expired. Please request the action again."
        if error == "missing":
            return "I have not heard a new confirmation. Nothing has been done."
        if error == "mismatch":
            return (
                f"Confirmation not recognized. Nothing has been done. "
                f"To proceed, say exactly: {_confirmation_instruction(pending.action)}."
            )
        state.pending = None

    if pending.action == "email":
        return await send_email_now(**pending.details)
    if pending.action == "sms":
        return await send_sms_now(**pending.details)
    return await asyncio.to_thread(perform_system_action, pending.action)


@function_tool
async def cancel_pending_action(ctx: RunContext[Any]) -> str:
    """Discard a pending draft or system action without executing it."""
    session_key = _session_key(ctx)
    with _lock:
        state = _states.get(session_key)
        if not state or not state.pending:
            return "There is no pending action to cancel."
        state.pending = None
    return "Pending action cancelled. Nothing was sent or executed."
