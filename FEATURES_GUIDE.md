# 🚀 Jarvis v3.0 - New Features Guide

## ✅ 5 New Features Added

### 1. **System Information** (Jarvis_system_info.py)
Get real-time CPU, RAM, and disk usage
```
Voice Command: "moto, बता मेरे system की जानकारी" / "What's my system status?"
Tool: get_system_info()
Output: CPU %, RAM usage, Disk usage
```

### 2. **Email & SMS** (Jarvis_email.py)
Send emails and text messages
```
Voice Commands:
- "Send an email to user@example.com with subject 'Hello' and body 'Hi there'"
- "Send an SMS to +1234567890 saying 'Hello there'"

Tools:
- send_email(recipient, subject, body)
- send_sms(phone_number, message)

Requirements:
- Gmail: Set SENDER_EMAIL and SENDER_PASSWORD in .env
- SMS: Install twilio and set Twilio credentials in .env
```

### 3. **Calendar & Reminders** (Jarvis_calendar.py)
Schedule events and set reminders
```
Voice Commands:
- "Set a reminder 'Meeting with boss' for 30 minutes from now"
- "Get all reminders"
- "Schedule event 'Birthday party' on 2026-02-15 at 18:30"

Tools:
- set_reminder(title, minutes_from_now)
- get_reminders()
- schedule_event(event_name, date, time, description)
```

### 4. **News & Stocks** (Jarvis_news_stocks.py)
Fetch latest news and stock prices
```
Voice Commands:
- "Get latest technology news" / "क्या latest news है?"
- "What's the stock price of Apple?" / "AAPL का price बता"

Tools:
- get_news(topic, country) - Topics: technology, business, sports, health, science
- get_stock_price(symbol) - Stock ticker: AAPL, GOOGL, MSFT, etc.

Requirements:
- NEWS_API_KEY from newsapi.org
- ALPHA_VANTAGE_API_KEY from alphavantage.co
```

### 5. **Screenshots & Recording** (Jarvis_screenshot.py)
Capture screen and record screen activity
```
Voice Commands:
- "Take a screenshot" / "स्क्रीनशॉट ले"
- "Start recording for 30 seconds" / "स्क्रीन record कर 30 सेकंड के लिए"
- "Extract text from screen" / "स्क्रीन से text निकाल"

Tools:
- take_screenshot(filename) - Saves to ~/Screenshots/
- start_recording(duration) - Saves to ~/Videos/Jarvis_Recordings/
- get_screen_text() - Uses OCR to extract text

Requirements:
- Pillow: pip install Pillow
- FFmpeg: https://ffmpeg.org/ (for recording)
- Tesseract: For OCR text extraction (pip install pytesseract)
```

---

## 🔧 Setup Instructions

### Required Installations
```bash
# Basic dependencies
pip install psutil  # For system info
pip install requests  # For news and stock API

# Optional (for advanced features)
pip install Pillow  # For screenshots
pip install twilio  # For SMS
pip install pytesseract  # For OCR
```

### Environment Variables (.env)
```
# System Info - No setup needed
# Built-in functionality

# Email Setup (Gmail)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password  # Use App Password, not regular password

# SMS Setup (Twilio)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

# News API
NEWS_API_KEY=your_free_key_from_newsapi.org

# Stock API
ALPHA_VANTAGE_API_KEY=your_free_key_from_alphavantage.co
```

---

## 📝 Files Modified/Created

| File | Type | Purpose |
|------|------|---------|
| `Jarvis_system_info.py` | NEW | System monitoring |
| `Jarvis_email.py` | NEW | Email & SMS |
| `Jarvis_calendar.py` | NEW | Reminders & events |
| `Jarvis_news_stocks.py` | NEW | News & stocks |
| `Jarvis_screenshot.py` | NEW | Screenshots & recording |
| `agent.py` | MODIFIED | Added imports & tools |
| `Jarvis_prompts.py` | MODIFIED | Updated instructions |
| `.env` | MODIFIED | Added API keys |

---

## 🎯 How It Works

1. **Voice Input** → User speaks to Jarvis
2. **LLM Processing** → Google Gemini understands intent
3. **Tool Selection** → Selects appropriate tool function
4. **Execution** → Tool executes the requested task
5. **Voice Output** → Result is spoken back to user

---

## 🧪 Testing

Run your agent:
```bash
# Activate venv
& C:\Users\goura\OneDrive\Desktop\Jarvis.v3.0-main-main\venv\Scripts\Activate.ps1

# Run agent
python .\agent.py console
```

Try these voice commands:
- "बता मेरे system की जानकारी" (Get system info)
- "Latest news बता technology के बारे में" (Get news)
- "AAPL का stock price क्या है?" (Get stock price)
- "एक रिमाइंडर सेट कर 10 minutes के लिए" (Set reminder)
- "स्क्रीनशॉट ले" (Take screenshot)

---

## 📞 Support

For issues:
1. Check API keys are correctly set in `.env`
2. Ensure all dependencies are installed
3. Check internet connection for API calls
4. Verify voice input is working

---

## 🔐 Security Notes

- ⚠️ Never commit `.env` file to git (add to .gitignore)
- Use App Passwords for Gmail, not regular password
- Keep API keys private
- Be careful with SMS functionality (may incur costs)

---

**Created:** January 25, 2026
**Version:** Jarvis v3.0
**Creator:** Anmol Gour
