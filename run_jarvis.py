"""Start the Jarvis LiveKit worker and its browser frontend together."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
REQUIRED_LIVEKIT_SETTINGS = (
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
)


def stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    if os.name == "nt":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except (AttributeError, OSError, ValueError):
            process.terminate()
    else:
        process.terminate()

    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def wait_for_frontend(
    process: subprocess.Popen[bytes],
    frontend_url: str,
    timeout: float = 15,
) -> None:
    deadline = time.monotonic() + timeout
    health_url = f"{frontend_url}/api/health"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Frontend server exited with code {process.returncode}.")
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    raise RuntimeError(f"Frontend server did not become ready at {health_url}.")


def main() -> int:
    load_dotenv(ROOT / ".env", override=True)
    missing_settings = [name for name in REQUIRED_LIVEKIT_SETTINGS if not os.getenv(name)]
    if missing_settings:
        print(
            "Missing required settings in .env: " + ", ".join(missing_settings),
            file=sys.stderr,
        )
        return 1

    try:
        port = int(os.getenv("JARVIS_WEB_PORT", "8000"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        print("JARVIS_WEB_PORT must be a valid port between 1 and 65535.", file=sys.stderr)
        return 1
    frontend_url = f"http://127.0.0.1:{port}"

    creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        print("Starting Jarvis LiveKit agent worker...", flush=True)
        worker = subprocess.Popen(
            [sys.executable, str(ROOT / "agent.py"), "start"],
            cwd=ROOT,
            env=os.environ.copy(),
            creationflags=creation_flags,
        )
        processes.append(("agent worker", worker))

        print("Starting Jarvis frontend and token server...", flush=True)
        frontend = subprocess.Popen(
            [sys.executable, str(ROOT / "web_server.py")],
            cwd=ROOT,
            env=os.environ.copy(),
            creationflags=creation_flags,
        )
        processes.append(("frontend server", frontend))
        wait_for_frontend(frontend, frontend_url)

        print(f"Jarvis is running at {frontend_url}", flush=True)
        print("Keep this window open. Press Ctrl+C to stop the frontend and agent.", flush=True)
        webbrowser.open(frontend_url)

        while True:
            for name, process in processes:
                exit_code = process.poll()
                if exit_code is not None:
                    print(f"The {name} exited with code {exit_code}. Stopping Jarvis.", flush=True)
                    return exit_code or 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping Jarvis...", flush=True)
        return 0
    except (OSError, RuntimeError) as error:
        print(f"Could not start Jarvis: {error}", file=sys.stderr, flush=True)
        return 1
    finally:
        for _, process in reversed(processes):
            stop_process(process)


if __name__ == "__main__":
    raise SystemExit(main())
