import logging
import platform
import subprocess

from livekit.agents import function_tool

logger = logging.getLogger(__name__)

_SYSTEM_COMMANDS = {
    "shutdown": ["shutdown", "/s", "/t", "0"],
    "restart": ["shutdown", "/r", "/t", "0"],
    "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
    "lock": ["rundll32.exe", "user32.dll,LockWorkStation"],
    "logout": ["shutdown", "/l"],
}


def perform_system_action(action: str) -> str:
    """Execute an allowlisted Windows system action after confirmation."""
    if platform.system() != "Windows":
        return "System power actions are currently supported only on Windows."
    command = _SYSTEM_COMMANDS.get(action)
    if command is None:
        return f"Unsupported system action: {action}."

    try:
        subprocess.run(command, check=True, timeout=15, capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError) as exc:
        logger.error("System action %s failed (%s)", action, type(exc).__name__)
        return f"Windows could not start the {action} action ({type(exc).__name__})."

    return f"Windows accepted the {action} request."


@function_tool
async def cancel_shutdown() -> str:
    """Cancel a scheduled Windows shutdown or restart."""
    if platform.system() != "Windows":
        return "Cancelling scheduled shutdowns is supported only on Windows."
    try:
        subprocess.run(["shutdown", "/a"], check=True, timeout=15, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        return f"Windows did not cancel a scheduled shutdown (exit code {exc.returncode})."
    except (OSError, subprocess.SubprocessError) as exc:
        logger.error("Cancel shutdown failed (%s)", type(exc).__name__)
        return f"Windows could not cancel the shutdown ({type(exc).__name__})."
    return "Scheduled shutdown cancelled."


@function_tool
async def system_status() -> str:
    """Report the operating system used by Jarvis."""
    return f"Jarvis is running on {platform.system()}."
