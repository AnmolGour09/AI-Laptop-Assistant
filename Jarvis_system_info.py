import asyncio
import psutil
import logging
from pathlib import Path
from livekit.agents import function_tool

logger = logging.getLogger(__name__)

@function_tool
async def get_system_info() -> str:
    """Get current CPU, RAM, and disk usage information"""
    try:
        cpu_percent = await asyncio.to_thread(psutil.cpu_percent, interval=0.25)

        # RAM usage
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_gb = ram.used / (1024**3)
        ram_total_gb = ram.total / (1024**3)
        
        # Disk usage
        disk = psutil.disk_usage(Path.home().anchor)
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        result = f"""
System Information:
- CPU Usage: {cpu_percent}%
- RAM Usage: {ram_percent}% ({ram_used_gb:.2f}GB / {ram_total_gb:.2f}GB)
- Disk Usage: {disk_percent}% ({disk_used_gb:.2f}GB / {disk_total_gb:.2f}GB)
"""
        logger.info(f"System info retrieved: CPU {cpu_percent}%, RAM {ram_percent}%, Disk {disk_percent}%")
        return result.strip()
    
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return f"Error retrieving system information: {str(e)}"
