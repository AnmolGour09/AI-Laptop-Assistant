import os
import subprocess
import webbrowser
import logging
import platform
from livekit.agents import function_tool
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
logger = logging.getLogger(__name__)

@function_tool
async def open_telegram() -> str:
    """Open Telegram application on the system"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Try to open Telegram from common Windows locations
            telegram_paths = [
                "C:\\Users\\{user}\\AppData\\Local\\Telegram Desktop\\Telegram.exe",
                "C:\\Program Files\\Telegram Desktop\\Telegram.exe",
                "C:\\Program Files (x86)\\Telegram Desktop\\Telegram.exe",
            ]
            
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            telegram_paths[0] = telegram_paths[0].format(user=username)
            
            opened = False
            for path in telegram_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    opened = True
                    break
            
            if not opened:
                # Try using the app protocol
                webbrowser.open("tg://")
                opened = True
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "Telegram"])
            opened = True
        
        elif system == "Linux":
            subprocess.Popen(["telegram-desktop"])
            opened = True
        
        result = "Telegram application opened"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening Telegram: {str(e)}. Make sure Telegram is installed."
        logger.error(error_msg)
        return error_msg

@function_tool
async def send_telegram_message(contact_name: str, message: str) -> str:
    """Send a text message via Telegram to a contact
    
    Args:
        contact_name: Name of the contact or phone number
        message: Message text to send
    """
    try:
        # URL encode the message
        encoded_message = quote(message)
        
        # Telegram Deep Link - opens chat with contact
        # Note: This opens the chat, you need to manually send or use bot API for automation
        telegram_url = f"tg://resolve?domain={contact_name}"
        
        logger.info(f"Opening Telegram chat with {contact_name}")
        webbrowser.open(telegram_url)
        
        result = f"Opening Telegram chat with '{contact_name}'. Please send: '{message}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error sending Telegram message: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def send_telegram_message_phone(phone_number: str, message: str) -> str:
    """Send a message via Telegram using phone number
    
    Args:
        phone_number: Phone number of the contact (with country code, e.g., +1234567890)
        message: Message text to send
    """
    try:
        # URL encode the message
        encoded_message = quote(message)
        
        # Clean phone number
        phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        
        # Telegram Deep Link
        telegram_url = f"tg://user?phone={phone}"
        
        logger.info(f"Opening Telegram chat with {phone_number}")
        webbrowser.open(telegram_url)
        
        result = f"Opening Telegram chat with '{phone_number}'. Please send: '{message}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error sending Telegram message: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def open_telegram_group(group_name: str) -> str:
    """Open a Telegram group or channel
    
    Args:
        group_name: Name of the group or channel (without @)
    """
    try:
        # Remove @ if provided
        group = group_name.lstrip("@")
        
        # Telegram Deep Link for groups/channels
        telegram_url = f"tg://resolve?domain={group}"
        
        logger.info(f"Opening Telegram group/channel: {group_name}")
        webbrowser.open(telegram_url)
        
        result = f"Opening Telegram group/channel: {group_name}"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening Telegram group: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def open_telegram_web() -> str:
    """Open Telegram Web (telegram.org web version)"""
    try:
        telegram_url = "https://web.telegram.org/"
        
        logger.info("Opening Telegram Web")
        webbrowser.open(telegram_url)
        
        result = "Opening Telegram Web in browser"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening Telegram Web: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def open_telegram_channel(channel_name: str) -> str:
    """Open a specific Telegram channel
    
    Args:
        channel_name: Name of the channel (without @)
    """
    try:
        # Remove @ if provided
        channel = channel_name.lstrip("@")
        
        # Telegram Deep Link
        telegram_url = f"tg://resolve?domain={channel}"
        
        logger.info(f"Opening Telegram channel: {channel_name}")
        webbrowser.open(telegram_url)
        
        result = f"Opening Telegram channel: {channel_name}"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening Telegram channel: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def search_telegram_contact(query: str) -> str:
    """Search for a contact in Telegram
    
    Args:
        query: Contact name or username to search
    """
    try:
        logger.info(f"Searching Telegram for: {query}")
        
        # Open Telegram and search (user will need to type query manually in most cases)
        result = f"Open Telegram and search for '{query}' in your contacts. Then say: 'Send message to [name]'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error searching Telegram: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def telegram_status() -> str:
    """Check and return Telegram availability status"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Check if Telegram is installed
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            telegram_path = f"C:\\Users\\{username}\\AppData\\Local\\Telegram Desktop\\Telegram.exe"
            if os.path.exists(telegram_path):
                return "✅ Telegram is installed and ready. You can use voice commands to send messages."
            else:
                return "⚠️ Telegram app not found. Install Telegram from https://telegram.org/ to enable full features."
        
        elif system == "Darwin":
            result = "Telegram ready on macOS. Use voice commands to send messages."
            return result
        
        elif system == "Linux":
            result = "Telegram ready on Linux. Use voice commands to send messages."
            return result
        
        return "Telegram status: Ready"
    
    except Exception as e:
        logger.error(f"Error checking Telegram status: {str(e)}")
        return "Error checking Telegram status. Try installing Telegram."
