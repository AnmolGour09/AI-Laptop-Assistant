# ⚡ Installation & Setup Guide - New Features

## 📦 Step 1: Install Required Packages

```powershell
# Run from the project root. Activate the virtual environment first.
& .\venv\Scripts\Activate.ps1

# Install the new dependencies
pip install psutil Pillow

# Optional (for advanced features)
pip install twilio pytesseract
```

## 🔑 Step 2: Configure API Keys (in `.env` file)

### Web Search
Jarvis uses DuckDuckGo as a backup automatically. For Google results, `GOOGLE_SEARCH_API_KEY` and `SEARCH_ENGINE_ID` must be set in `.env`, and the Custom Search API must be enabled for the same Google Cloud project. A configured key alone is not sufficient. If Google is disabled or unavailable, the agent tries the backup provider.

### A. System Info (✅ No setup needed)
- Works out of the box!

### B. Email (Optional)
For Gmail, enable 2-Step Verification and create a Google App Password. Do not use your regular account password or enable the retired "less secure apps" setting. Add these values to the project-root `.env` file:
```
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=your_app_password
```
Jarvis reads the recipient, subject, and full message back first. To send, say the exact confirmation phrase it requests (for example, "confirm email"). The confirmation must be spoken in a separate turn. Delivery is reported only after the SMTP server accepts the message.

### C. SMS via Twilio (Optional)
1. Sign up at https://www.twilio.com/
2. Get your Account SID, Auth Token, and phone number
3. Add to `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```
Jarvis reads the destination and message back, then requires the separate phrase "confirm sms" before calling Twilio. A successful tool response means Twilio accepted the message; it does not guarantee delivery to the recipient.

### D. Confirmed Windows system actions
Shutdown, restart, sleep, lock, and logout are not executed directly from a request. Jarvis asks for a separate, exact confirmation such as "confirm shutdown" or "confirm lock". If the request is cancelled or the confirmation is not recognized, the action is not run. Windows must accept the action command before Jarvis reports that it was accepted.

### E. News API (Optional)
1. Get free key from https://newsapi.org/
2. Add to `.env`:
```
NEWS_API_KEY=your_newsapi_key_here
```

### F. Stock Market API (Optional)
1. Get free key from https://www.alphavantage.co/
2. Add to `.env`:
```
ALPHA_VANTAGE_API_KEY=your_free_key_here
```

## 🎮 Step 3: Run the Backend and Frontend

```powershell
.\run.bat
```
This starts the LiveKit backend worker and frontend/token server together. Keep this terminal open while using the web interface.

## 🗣️ Step 4: Voice Commands to Try

### System Info
```
"Jarvis, बता मेरे system की जानकारी"
"What's my CPU usage?"
"Show me RAM usage"
```

### Email
```
"Email john@example.com with subject Hello and body Hi there"
"Confirm email"
```
The first request only stages a draft. Jarvis reads it back and tells you the required confirmation phrase; say that phrase in a new turn only after verifying the details.

### SMS (if configured)
```
"Prepare an SMS to +1234567890 saying hello"
"Confirm SMS"
```

### Confirmed system actions
```
"Shut down this computer"
"Confirm shutdown"
```

### Calendar & Reminders
```
"Set reminder 'Meeting' for 30 minutes"
"Show all reminders"
"Schedule meeting on 2026-12-15 at 14:00"
```

### News & Stocks
```
"Latest technology news बता"
"Get business news for India"
"What's the stock price of Apple?"
"Tell me GOOGL stock price"
```

### Screenshots
```
"Take a screenshot"
"स्क्रीनशॉट ले"
"Record screen for 30 seconds"
"Extract text from screen"
```

## Current integration limits

- Email and SMS sending are confirmation-gated; actual delivery requires valid provider credentials and a successful provider response.
- WhatsApp and Telegram message sending are not enabled in the voice agent. The existing modules only open links or provide manual guidance and cannot verify delivery.
- YouTube in Brave opens the home page or search results and leaves video selection to the user. It does not auto-select a video.
- Calendar reminders are process-memory only, and browser form automation/account integrations are not currently implemented.
- File deletion is disabled because the current file tool searches a hard-coded drive and does not yet have safe path-specific confirmation.

| Capability | Current status |
| --- | --- |
| Voice/frontend | LiveKit browser connection exists; no wake-word detector. Voice accuracy and continuous live speech have not been fully tested. |
| YouTube | Can open Brave to the YouTube home page or search results; you choose the video manually. Automatic video selection and playback controls are not implemented. |
| WhatsApp/Telegram | Can open apps, links, or web clients; contact resolution, sending, and delivery verification are unavailable. |
| Browser | Search is available; general tab control, form filling, page extraction, and submit approval are not implemented. |
| Windows apps/system | App launch is restricted to configured names. Power actions require action-specific spoken confirmation. Real app launch and power actions were not run during these checks. |
| Files | Existing search uses a hard-coded `D:\` root; file deletion is disabled. Safe cross-drive search, copy/move, and path-specific file actions are not complete. |
| Email/SMS | Email SMTP and Twilio SMS are available after confirmation; no inbox reading, search, or reply workflow. Provider delivery was not tested. |
| Calendar/productivity | Reminders and events are in-memory only; no persistence or authorized calendar sync. |
| Weather/news/stocks | API-backed tools exist, but location fallback, source/timestamp reporting, and live data behavior need further verification. |
| System info/screenshots/OCR | System information was tested previously; screenshot, recording, and OCR paths still depend on local tools and have not been fully tested. |
| Multi-step/tool reasoning | The model can invoke multiple tools, but there is no durable task planner or guaranteed step-by-step verification. |

## Validate the confirmation safeguards

From the project root, run:
```powershell
& .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_confirmations.py" -v
& .\venv\Scripts\python.exe -m compileall -q agent.py Jarvis_confirmations.py Jarvis_email.py Jarvis_system_control.py Jarvis_window_CTRL.py keyboard_mouse_CTRL.py
```

These checks validate phrase/expiry/session isolation, tool exposure, and Python syntax. They do not send a real email/SMS, execute a Windows power action, or verify that an installed app launched. Verify those integrations only with test accounts and after reading Jarvis's spoken confirmation prompt.

### Open YouTube in Brave

Brave must be installed in a standard Windows location or discoverable as `brave.exe` on `PATH`. Try:
```
"Open YouTube in Brave"
"Open YouTube in Brave and search Java interview questions"
```
Jarvis opens the homepage or search results without asking for confirmation. You select the video yourself; Jarvis does not start a video automatically.

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'psutil'` | Run `pip install psutil` |
| "API key not found" error | Check .env file is in the correct directory |
| FFmpeg not found (for recording) | Install from https://ffmpeg.org/ |
| SMS not working | Check Twilio credentials in .env |
| Tesseract not found (for OCR) | Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki |

## 📞 Need Help?

1. Check FEATURES_GUIDE.md for detailed info
2. Verify .env file has correct format
3. Ensure API keys are valid
4. Check internet connection for API calls

---

**Ready to use!** Start the backend and frontend together with `.\run.bat`.

## Run Jarvis Frontend and Backend Together

A connected Jarvis dashboard is available in `frontend\`. Start both the LiveKit agent backend and frontend together from the project folder:

```powershell
.\run.bat
```

The launcher starts `agent.py start` and the local frontend/token server, then opens `http://127.0.0.1:8000` in your browser. Keep the terminal window open while using Jarvis; press **Ctrl+C** to stop both processes. Ensure `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are set in `.env`. The local web server issues short-lived, room-scoped browser tokens without exposing the API secret. Click **Connect** and allow microphone access. The microphone stays muted while Jarvis gives its welcome, then automatically turns on. If the welcome cannot be generated, the page reports the failure and enables the microphone so you are not left muted. After a task is recognized, Jarvis leaves the mic on for three seconds, mutes it while processing and speaking, and turns it back on when the response is complete. The status badge and mic button label show whether Jarvis is introducing itself, listening, or working. You can still mute/unmute manually while Jarvis is listening. The agent listens for English, Hindi, and Hinglish, and asks for clarification when important details are unclear. The browser loads the LiveKit client from jsDelivr, so the page needs internet access.

Do not open `frontend\index.html` directly as a `file://` page. It is only a standalone preview and cannot connect to the agent. If the browser is on a `file://` URL, close it, run `.\run.bat`, and use `http://127.0.0.1:8000/`.

If PowerShell script execution is disabled, `.\run.bat` works without changing the execution policy. You can also run `& .\venv\Scripts\python.exe .\run_jarvis.py` directly. For manual separate-terminal startup, use `& .\venv\Scripts\python.exe .\agent.py start` for the worker and `.\run_web.ps1` for the frontend. `python .\agent.py console` is local console mode and does not accept browser room connections.
