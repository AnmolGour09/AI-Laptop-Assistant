import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Awaitable, Callable

# CRITICAL: Load .env BEFORE any other imports
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
loaded = load_dotenv(env_path, override=True)

# If dotenv didn't work, manually read the file
if not os.getenv('LIVEKIT_URL'):
    if env_path.exists():
        with open(env_path, 'rb') as f:
            content = f.read().decode('utf-8-sig')  # Handle BOM
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value:  # Only set if value is not empty
                        os.environ[key] = value

# Final check
if not os.getenv('LIVEKIT_URL'):
    print("ERROR: LIVEKIT_URL not set. Check your .env file.")
    sys.exit(1)

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from google.genai import types as google_types
from livekit.plugins import (
    google,
    noise_cancellation,
)
from Jarvis_prompts import behavior_prompts
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
from Jarvis_system_info import get_system_info
from Jarvis_browser import open_youtube_in_brave
from Jarvis_calendar import set_reminder, get_reminders, schedule_event
from Jarvis_news_stocks import get_news, get_stock_price
from Jarvis_screenshot import take_screenshot, start_recording, get_screen_text
from Jarvis_youtube import play_youtube_video, play_youtube_direct, play_youtube_playlist, play_youtube_music, youtube_autoplay_suggestions, youtube_trending, youtube_subscriptions, youtube_history
from Jarvis_telegram import open_telegram, open_telegram_group, open_telegram_web, open_telegram_channel, search_telegram_contact, telegram_status
from Jarvis_whatsapp import open_whatsapp, open_whatsapp_web, whatsapp_status_update, open_whatsapp_broadcast, whatsapp_status
from Jarvis_system_control import cancel_shutdown, system_status
from Jarvis_confirmations import (
    cancel_pending_action,
    clear_session_confirmation_state,
    confirm_pending_action,
    prepare_email,
    prepare_sms,
    record_user_transcript,
    request_system_action,
)

logger = logging.getLogger(__name__)

INTRO_INSTRUCTIONS = (
    "Give this exact short spoken welcome in Hindi: "
    "नमस्ते, मैं Jarvis हूँ। मैं सुन रहा हूँ—बताइए, मैं आपकी क्या मदद करूँ? "
    "Do not call tools or add any other text."
)


async def speak_session_intro(
    session: Any,
    publish_voice_status: Callable[[str], Awaitable[None]],
) -> bool:
    try:
        speech = session.generate_reply(
            instructions=INTRO_INSTRUCTIONS,
            tool_choice="none",
        )
        await speech
        if speech.exception() is not None:
            raise RuntimeError("Jarvis introduction speech failed") from speech.exception()
    except Exception:
        logger.exception("Jarvis introduction speech failed")
        await publish_voice_status("intro_failed")
        return False

    await publish_voice_status("intro_complete")
    return True


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=behavior_prompts,
                         tools=[
                            # Existing tools
                            google_search,
                            get_current_datetime,
                            get_weather,
                            open, #ये apps ओपन करने के लिए हैं
                            close, 
                            folder_file, #ये folder ओपन करने के लिए है
                            Play_file,  #ये file रन करने के लिए है जैसे कि MP4, MP3, PDF, PPT, img, png etc.
                            move_cursor_tool, #ये cursor move करने के लिए है
                            mouse_click_tool, #ये mouse click करने के लिए है
                            scroll_cursor_tool, #ये cursor scroll करने के लिए है
                            type_text_tool, #ये text type करने के लिए है
                            press_key_tool, #ये key press करने के लिए है
                            press_hotkey_tool, #ये hotkey press करने के लिए है
                            control_volume_tool, #ये volume control करने के लिए है
                            swipe_gesture_tool, #ये gesture wipe करने के लिए है
                            
                            # New tools
                            get_system_info, #सिस्टम की जानकारी (CPU, RAM, Disk)
                            prepare_email,
                            prepare_sms,
                            confirm_pending_action,
                            cancel_pending_action,
                            set_reminder, #रिमाइंडर सेट करने के लिए
                            get_reminders, #रिमाइंडर देखने के लिए
                            schedule_event, #इवेंट शेड्यूल करने के लिए
                            get_news, #समाचार प्राप्त करने के लिए
                            get_stock_price, #स्टॉक की कीमत के लिए
                            take_screenshot, #स्क्रीनशॉट लेने के लिए
                            start_recording, #स्क्रीन रिकॉर्ड करने के लिए
                            get_screen_text, #स्क्रीन से टेक्स्ट निकालने के लिए
                            
                            # YouTube tools
                            play_youtube_video, #YouTube पर वीडियो खोजने और चलाने के लिए
                            play_youtube_direct, #सीधे YouTube वीडियो ID से चलाने के लिए
                            play_youtube_playlist, #YouTube playlist चलाने के लिए
                            play_youtube_music, #संगीत खोजने के लिए
                            youtube_autoplay_suggestions, #YouTube होम पेज खोलने के लिए
                            youtube_trending, #ट्रेंडिंग वीडियो देखने के लिए
                            youtube_subscriptions, #सदस्यताओं को देखने के लिए
                            youtube_history, #देखने की history देखने के लिए
                            open_youtube_in_brave,
                            
                            # Telegram tools
                            open_telegram, #Telegram ऐप्लिकेशन खोलने के लिए
                            open_telegram_group, #Telegram समूह खोलने के लिए
                            open_telegram_web, #Telegram Web खोलने के लिए
                            open_telegram_channel, #Telegram चैनल खोलने के लिए
                            search_telegram_contact, #Telegram में संपर्क खोजने के लिए
                            telegram_status, #Telegram स्थिति जांचने के लिए
                            
                            # WhatsApp tools
                            open_whatsapp, #WhatsApp ऐप्लिकेशन खोलने के लिए
                            open_whatsapp_web, #WhatsApp Web खोलने के लिए
                            whatsapp_status_update, #WhatsApp स्थिति अपडेट करने के लिए
                            open_whatsapp_broadcast, #WhatsApp broadcast list खोलने के लिए
                            whatsapp_status, #WhatsApp स्थिति जांचने के लिए
                            
                            # System Control tools
                            request_system_action,
                            cancel_shutdown, #shutdown/restart को cancel करने के लिए
                            system_status, #सिस्टम की स्थिति check करने के लिए
                         ]
                         )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Charon",
            instructions=behavior_prompts,
            temperature=0.4,
            realtime_input_config=google_types.RealtimeInputConfig(
                automatic_activity_detection=google_types.AutomaticActivityDetection(
                    start_of_speech_sensitivity=google_types.StartSensitivity.START_SENSITIVITY_HIGH,
                    end_of_speech_sensitivity=google_types.EndSensitivity.END_SENSITIVITY_LOW,
                    prefix_padding_ms=300,
                    silence_duration_ms=550,
                )
            ),
        )
    )
    intro_complete = False
    assistant_is_processing = False

    async def publish_voice_status(status: str) -> None:
        try:
            await ctx.room.local_participant.send_text(
                json.dumps({"status": status}),
                topic="jarvis.voice",
            )
        except Exception:
            logger.exception("Could not publish voice status: %s", status)

    def on_user_transcript(event) -> None:
        record_user_transcript(id(session), event.transcript, event.is_final)
        if event.is_final and event.transcript.strip():
            asyncio.create_task(publish_voice_status("task_received"))

    def on_agent_state(event) -> None:
        nonlocal assistant_is_processing
        if not intro_complete:
            return

        if event.new_state == "thinking":
            assistant_is_processing = True
            asyncio.create_task(publish_voice_status("task_processing"))
        elif event.new_state == "speaking" and assistant_is_processing:
            asyncio.create_task(publish_voice_status("task_processing"))
        elif event.new_state in {"listening", "idle"} and assistant_is_processing:
            assistant_is_processing = False
            asyncio.create_task(publish_voice_status("task_complete"))

    session.on(
        "user_input_transcribed",
        on_user_transcript,
    )
    session.on("agent_state_changed", on_agent_state)
    session.on("close", lambda event: clear_session_confirmation_state(id(session)))
    
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=False,
        ),
    )

    await ctx.connect()
    await speak_session_intro(session, publish_voice_status)
    intro_complete = True

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
