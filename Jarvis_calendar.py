import os
import logging
from datetime import datetime, timedelta
from livekit.agents import function_tool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Simple in-memory reminders storage
reminders = []

@function_tool
async def set_reminder(title: str, minutes_from_now: int) -> str:
    """Set a reminder/event for a future time
    
    Args:
        title: Reminder title or event description
        minutes_from_now: Number of minutes until the reminder
    """
    try:
        reminder_time = datetime.now() + timedelta(minutes=minutes_from_now)
        
        reminder = {
            "title": title,
            "scheduled_time": reminder_time,
            "created_at": datetime.now()
        }
        reminders.append(reminder)
        
        result = f"Reminder set: '{title}' for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error setting reminder: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def get_reminders() -> str:
    """Get all upcoming reminders"""
    try:
        if not reminders:
            return "No reminders set."
        
        now = datetime.now()
        upcoming = [r for r in reminders if r["scheduled_time"] > now]
        
        if not upcoming:
            return "No upcoming reminders."
        
        reminder_list = "\n".join([
            f"- {r['title']} at {r['scheduled_time'].strftime('%H:%M:%S')}"
            for r in sorted(upcoming, key=lambda x: x['scheduled_time'])
        ])
        
        return f"Upcoming Reminders:\n{reminder_list}"
    
    except Exception as e:
        logger.error(f"Error getting reminders: {str(e)}")
        return f"Error retrieving reminders: {str(e)}"

@function_tool
async def schedule_event(event_name: str, date: str, time: str, description: str = "") -> str:
    """Schedule a calendar event
    
    Args:
        event_name: Name of the event
        date: Date in format YYYY-MM-DD
        time: Time in format HH:MM
        description: Optional event description
    """
    try:
        # Parse the date and time
        event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        
        event = {
            "name": event_name,
            "scheduled_time": event_datetime,
            "description": description,
            "created_at": datetime.now()
        }
        reminders.append(event)
        
        result = f"Event scheduled: '{event_name}' on {event_datetime.strftime('%Y-%m-%d at %H:%M')}"
        if description:
            result += f" - {description}"
        
        logger.info(result)
        return result
    
    except ValueError as e:
        error_msg = f"Error: Invalid date/time format. Use YYYY-MM-DD and HH:MM"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error scheduling event: {str(e)}"
        logger.error(error_msg)
        return error_msg
