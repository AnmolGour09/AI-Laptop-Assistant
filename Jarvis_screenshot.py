import os
import logging
from pathlib import Path
from livekit.agents import function_tool

logger = logging.getLogger(__name__)

@function_tool
async def take_screenshot(filename: str = "screenshot") -> str:
    """Take a screenshot of the current screen
    
    Args:
        filename: Name of the screenshot file (without extension)
    """
    try:
        from PIL import ImageGrab
        
        screenshots_dir = Path.home() / "Screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        filepath = screenshots_dir / f"{filename}.png"
        
        # Handle duplicate filenames
        counter = 1
        while filepath.exists():
            filepath = screenshots_dir / f"{filename}_{counter}.png"
            counter += 1
        
        logger.info(f"Taking screenshot: {filepath}")
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        
        result = f"Screenshot saved to {filepath}"
        logger.info(result)
        return result
    
    except ImportError:
        return "Error: Pillow library not installed. Run: pip install Pillow"
    except Exception as e:
        error_msg = f"Error taking screenshot: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def start_recording(duration: int = 30) -> str:
    """Start recording screen with audio
    
    Args:
        duration: Duration of recording in seconds (default: 30)
    """
    try:
        import subprocess
        from datetime import datetime
        
        recordings_dir = Path.home() / "Videos" / "Jarvis_Recordings"
        recordings_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = recordings_dir / f"recording_{timestamp}.mp4"
        
        # Using FFmpeg to record screen (Windows)
        cmd = [
            "ffmpeg",
            "-f", "gdigrab",
            "-framerate", "30",
            "-i", "desktop",
            "-f", "dshow",
            "-i", "audio=\"Microphone (Realtek(R) Audio)\"",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-t", str(duration),
            "-y",
            str(output_file)
        ]
        
        logger.info(f"Starting {duration}s screen recording: {output_file}")
        
        # Run FFmpeg in background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        result = f"Recording started for {duration} seconds. Saving to {output_file}"
        logger.info(result)
        return result
    
    except FileNotFoundError:
        return "Error: FFmpeg not installed. Install from https://ffmpeg.org/"
    except Exception as e:
        error_msg = f"Error starting recording: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def get_screen_text() -> str:
    """Extract text from current screen (OCR)"""
    try:
        from PIL import ImageGrab
        import pytesseract
        
        logger.info("Capturing screen text...")
        screenshot = ImageGrab.grab()
        
        text = pytesseract.image_to_string(screenshot)
        
        if not text.strip():
            return "No text detected on screen"
        
        return f"Text detected on screen:\n{text}"
    
    except ImportError as e:
        return f"Error: Required library not installed. Run: pip install pytesseract pillow"
    except Exception as e:
        error_msg = f"Error extracting screen text: {str(e)}"
        logger.error(error_msg)
        return error_msg
