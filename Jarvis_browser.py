import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlencode

from livekit.agents import function_tool

logger = logging.getLogger(__name__)


def find_brave_executable() -> Path | None:
    local_app_data = os.environ.get("LOCALAPPDATA")
    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe",
    ]
    if local_app_data:
        candidates.append(
            Path(local_app_data)
            / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe"
        )

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    executable = shutil.which("brave.exe")
    return Path(executable) if executable else None


@function_tool
async def open_youtube_in_brave(query: str = "") -> str:
    """Open YouTube in Brave, optionally showing search results for the user's query.

    Args:
        query: Optional YouTube search terms. YouTube will show results for the user to choose from.
    """
    if platform.system() != "Windows":
        return "Opening YouTube in Brave is currently supported on Windows."

    query = query.strip()
    if len(query) > 300:
        return "The YouTube search is too long. Please use 300 characters or fewer."

    brave = find_brave_executable()
    if brave is None:
        return "Brave was not found. Install Brave Browser, then try again."

    youtube_url = "https://www.youtube.com/"
    if query:
        youtube_url = f"{youtube_url}results?{urlencode({'search_query': query})}"

    try:
        subprocess.Popen([str(brave), youtube_url])
    except OSError as exc:
        logger.error("Unable to open YouTube in Brave (%s)", type(exc).__name__)
        return f"Could not start Brave ({type(exc).__name__})."

    if query:
        return f"Opened YouTube search results for “{query}” in Brave. Choose the video you want manually."
    return "Opened YouTube in Brave. Choose a video manually."
