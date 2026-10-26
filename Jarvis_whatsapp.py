import os
import subprocess
import webbrowser
import logging
import platform
import pyautogui
import time
from livekit.agents import function_tool
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
logger = logging.getLogger(__name__)

@function_tool
async def open_whatsapp() -> str:
    """Open WhatsApp application on the system"""
    try:
        system = platform.system()
        
        if system == "Windows":
            # Try to open WhatsApp from common Windows locations
            whatsapp_paths = [
                "C:\\Users\\{user}\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
                "C:\\Program Files\\WhatsApp\\WhatsApp.exe",
                "C:\\Program Files (x86)\\WhatsApp\\WhatsApp.exe",
            ]
            
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_paths[0] = whatsapp_paths[0].format(user=username)
            
            opened = False
            for path in whatsapp_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    opened = True
                    break
            
            if not opened:
                # Try using the app protocol
                webbrowser.open("whatsapp://")
                opened = True
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "WhatsApp"])
            opened = True
        
        elif system == "Linux":
            subprocess.Popen(["whatsapp-nativefier"])
            opened = True
        
        result = "WhatsApp application opened"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening WhatsApp: {str(e)}. Make sure WhatsApp is installed."
        logger.error(error_msg)
        return error_msg

@function_tool
async def send_whatsapp_message(contact_name: str, message: str) -> str:
    """Send a text message via WhatsApp to a contact
    
    Args:
        contact_name: Name of the contact saved in WhatsApp
        message: Message text to send
    """
    try:
        # URL encode the message
        encoded_message = quote(message)
        
        # WhatsApp Deep Link - opens chat with contact
        # Note: Contact must be saved in WhatsApp
        whatsapp_url = f"whatsapp://send?text={encoded_message}"
        
        logger.info(f"Opening WhatsApp chat to send message to {contact_name}")
        webbrowser.open(whatsapp_url)
        
        result = f"Opening WhatsApp to message '{contact_name}'. Please select contact and send: '{message}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error sending WhatsApp message: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def send_whatsapp_message_phone(phone_number: str, message: str) -> str:
    """Send a message via WhatsApp using phone number
    
    Args:
        phone_number: Phone number of the contact (with country code, e.g., +1234567890)
        message: Message text to send
    """
    try:
        # URL encode the message
        encoded_message = quote(message)
        
        # Clean phone number (remove +, -, spaces)
        phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        
        # WhatsApp Deep Link format
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
        
        logger.info(f"Opening WhatsApp chat with {phone_number}")
        webbrowser.open(whatsapp_url)
        
        result = f"Opening WhatsApp to message '{phone_number}'. Message ready: '{message}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error sending WhatsApp message: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def open_whatsapp_web() -> str:
    """Open WhatsApp Web (web.whatsapp.com)"""
    try:
        whatsapp_url = "https://web.whatsapp.com/"
        
        logger.info("Opening WhatsApp Web")
        webbrowser.open(whatsapp_url)
        
        result = "Opening WhatsApp Web. Scan QR code to log in."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening WhatsApp Web: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def send_whatsapp_group_message(group_name: str, message: str) -> str:
    """Send a message to a WhatsApp group
    
    Args:
        group_name: Name of the group saved in WhatsApp
        message: Message text to send
    """
    try:
        # URL encode the message
        encoded_message = quote(message)
        
        # WhatsApp Deep Link
        whatsapp_url = f"whatsapp://send?text={encoded_message}"
        
        logger.info(f"Opening WhatsApp to send message to group '{group_name}'")
        webbrowser.open(whatsapp_url)
        
        result = f"Opening WhatsApp. Select group '{group_name}' and send: '{message}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error sending WhatsApp group message: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_status_update(status_text: str) -> str:
    """Update WhatsApp status
    
    Args:
        status_text: Status message text
    """
    try:
        logger.info(f"Opening WhatsApp to update status: {status_text}")
        
        # Open WhatsApp, user will manually update status
        result = f"Open WhatsApp and go to Status tab. Update status to: '{status_text}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error with status update: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def open_whatsapp_broadcast(list_name: str) -> str:
    """Open WhatsApp broadcast list
    
    Args:
        list_name: Name of the broadcast list
    """
    try:
        logger.info(f"Opening WhatsApp broadcast list: {list_name}")
        
        result = f"Open WhatsApp. Go to Chats and find broadcast list '{list_name}'"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening broadcast list: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_call(contact_name: str) -> str:
    """Make a WhatsApp voice call to a contact
    
    Args:
        contact_name: Name of the contact to call
    """
    try:
        logger.info(f"Initiating WhatsApp call to {contact_name}")
        
        system = platform.system()
        
        # Open WhatsApp app directly for better call support
        if system == "Windows":
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_path = f"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            
            if os.path.exists(whatsapp_path):
                subprocess.Popen(whatsapp_path)
                result = f"WhatsApp खुल गया। अब {contact_name} को खोजें और call button दबाएं।"
                logger.info(result)
                return result
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "WhatsApp"])
            result = f"WhatsApp खुल गया। अब {contact_name} को खोजें और call करें।"
            logger.info(result)
            return result
        
        # Fallback
        result = f"WhatsApp खोलें। {contact_name} को खोजें और voice call दबाएं।"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error making WhatsApp call: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_video_call(phone_number: str) -> str:
    """Make a WhatsApp video call to a contact
    
    Args:
        phone_number: Phone number of the contact
    """
    try:
        # Clean phone number
        phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
        
        logger.info(f"Initiating WhatsApp video call to {phone_number}")
        
        system = platform.system()
        
        # First, open WhatsApp app directly
        if system == "Windows":
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_path = f"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            
            if os.path.exists(whatsapp_path):
                subprocess.Popen(whatsapp_path)
                result = f"WhatsApp खुल गया। अब {phone_number} को खोजें और video call button दबाएं।"
                logger.info(result)
                return result
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "WhatsApp"])
            result = f"WhatsApp खुल गया। {phone_number} को खोजें और video call करें।"
            logger.info(result)
            return result
        
        # Fallback to opening contact in WhatsApp
        webbrowser.open(f"https://wa.me/{phone}")
        result = f"WhatsApp/Web खुल गया। {phone_number} को खोजें और video call करें।"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error making WhatsApp video call: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_status() -> str:
    """Check and return WhatsApp availability status"""
    try:
        system = platform.system()
        
        if system == "Windows":
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_path = f"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            if os.path.exists(whatsapp_path):
                return "✅ WhatsApp is installed and ready. You can use voice commands to send messages."
            else:
                return "⚠️ WhatsApp app not found. Install WhatsApp from https://whatsapp.com/ to enable full features."
        
        elif system == "Darwin":
            return "WhatsApp ready on macOS. Use voice commands to send messages."
        
        elif system == "Linux":
            return "WhatsApp ready on Linux. Use voice commands to send messages."
        
        return "WhatsApp status: Ready"
    
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {str(e)}")
        return "Error checking WhatsApp status. Try installing WhatsApp."

@function_tool
async def whatsapp_auto_video_call(contact_name: str) -> str:
    """Automatically find and click video call button for a contact using keyboard navigation
    
    Args:
        contact_name: Name of the contact to video call
    """
    try:
        logger.info(f"Starting automatic video call to {contact_name}")
        
        system = platform.system()
        
        # Open WhatsApp
        if system == "Windows":
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_path = f"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            
            if os.path.exists(whatsapp_path):
                subprocess.Popen(whatsapp_path)
                time.sleep(3)  # Wait for app to open
                
                logger.info(f"Searching for contact: {contact_name}")
                
                # Use Ctrl+F to open search
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                
                # Type contact name
                for char in contact_name:
                    pyautogui.typewrite(char)
                    time.sleep(0.05)
                time.sleep(1.5)
                
                # Press Enter to select first result
                pyautogui.press('enter')
                time.sleep(2)
                
                # Use Tab to navigate to video call button (more reliable than hardcoded coordinates)
                # Typically: Tab navigates through top buttons
                pyautogui.press('tab')
                time.sleep(0.3)
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # Press Enter to activate video call button
                pyautogui.press('enter')
                time.sleep(1)
                
                result = f"✅ WhatsApp video call को {contact_name} से connect कर रहे हैं..."
                logger.info(result)
                return result
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "WhatsApp"])
            time.sleep(3)
            
            # Use Cmd+F to search
            pyautogui.hotkey('cmd', 'f')
            time.sleep(1)
            for char in contact_name:
                pyautogui.typewrite(char)
                time.sleep(0.05)
            time.sleep(1.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Navigate using Tab and press Enter
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(1)
            
            result = f"✅ WhatsApp video call को {contact_name} से connect कर रहे हैं..."
            logger.info(result)
            return result
        
        result = f"⚠️ Auto video call के लिए WhatsApp app install करें"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error in auto video call: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_auto_voice_call(contact_name: str) -> str:
    """Automatically find and click voice call button for a contact using keyboard navigation
    
    Args:
        contact_name: Name of the contact to call
    """
    try:
        logger.info(f"Starting automatic voice call to {contact_name}")
        
        system = platform.system()
        
        # Open WhatsApp
        if system == "Windows":
            username = os.getenv("USERNAME", os.path.expanduser("~").split("\\")[-1])
            whatsapp_path = f"C:\\Users\\{username}\\AppData\\Local\\WhatsApp\\WhatsApp.exe"
            
            if os.path.exists(whatsapp_path):
                subprocess.Popen(whatsapp_path)
                time.sleep(3)
                
                logger.info(f"Searching for contact: {contact_name}")
                
                # Use Ctrl+F to open search
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(1)
                
                # Type contact name
                for char in contact_name:
                    pyautogui.typewrite(char)
                    time.sleep(0.05)
                time.sleep(1.5)
                
                # Press Enter to select first result
                pyautogui.press('enter')
                time.sleep(2)
                
                # Use Tab to navigate to voice call button
                pyautogui.press('tab')
                time.sleep(0.3)
                
                # Press Enter to activate voice call button
                pyautogui.press('enter')
                time.sleep(1)
                
                result = f"✅ WhatsApp voice call को {contact_name} से connect कर रहे हैं..."
                logger.info(result)
                return result
        
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", "WhatsApp"])
            time.sleep(3)
            
            # Use Cmd+F to search
            pyautogui.hotkey('cmd', 'f')
            time.sleep(1)
            for char in contact_name:
                pyautogui.typewrite(char)
                time.sleep(0.05)
            time.sleep(1.5)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Navigate using Tab and press Enter
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(1)
            
            result = f"✅ WhatsApp voice call को {contact_name} से connect कर रहे हैं..."
            logger.info(result)
            return result
        
        result = f"⚠️ Auto voice call के लिए WhatsApp app install करें"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error in auto voice call: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_click_video_button() -> str:
    """Click the video call button using keyboard navigation (Tab + Enter)"""
    try:
        logger.info("Activating video call button via keyboard")
        
        # Navigate to video call button with Tab presses
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('tab')
        time.sleep(0.2)
        
        # Activate it
        pyautogui.press('enter')
        time.sleep(1)
        
        result = "✅ Video call button activate हो गया"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error clicking video button: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def whatsapp_click_voice_button() -> str:
    """Click the voice call button using keyboard navigation (Tab + Enter)"""
    try:
        logger.info("Activating voice call button via keyboard")
        
        # Navigate to voice call button with Tab press
        pyautogui.press('tab')
        time.sleep(0.2)
        
        # Activate it
        pyautogui.press('enter')
        time.sleep(1)
        
        result = "✅ Voice call button activate हो गया"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error clicking voice button: {str(e)}"
        logger.error(error_msg)
        return error_msg
