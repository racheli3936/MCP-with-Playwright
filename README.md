# MCP Weather Agent

פרויקט זה בונה ממשק `Host` שמשתמש ב־MCP כדי להריץ שני כלי מזג אוויר נפרדים:

- `weather_USA.py` — מקבל תחזית ואלרטים עבור ארצות הברית באמצעות API של NWS
- `weather_Israel.py` — מבצע אוטומציה ב־Playwright באתר `weather2day.co.il` כדי לקבל תחזית עבור עיר בישראל

## מה הפרויקט עושה

ה־Host טוען את כל ה־MCP tools הזמינים מכלים חיצוניים ומאפשר לשאול שאלות חופשיות בצ׳אט. כאשר השאלה קשורה למזג אוויר, ה־LLM יכול לבחור לבצע קריאת כלי ולהחזיר תשובה מבוססת.

## קבצים מרכזיים

- `host.py` — ה־Host של ה־MCP שמרכז את כל הכלים ומתקשר עם OpenAI
- `weather_USA.py` — כלי להזמנת מידע מזג אוויר בארה"ב
- `weather_Israel.py` — כלי אוטומטי ב־Playwright להזמנת מזג אוויר בישראל
- `.env` — קובץ עם משתני סביבה
- `pyproject.toml` — תלויות הפרויקט

## תלויות

הפרויקט דורש:

- Python 3.13+
- `openai`
- `mcp`
- `python-dotenv`
- `playwright`

## התקנה

ב־Windows:

```powershell
cd c:\Users\user1\Desktop\תכנות\תשפו\dovrot-ai-projects-master\8-mcp\project-template
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

אם אין `requirements.txt`, התקין מתוך `pyproject.toml` או ידנית:

```powershell
pip install openai mcp python-dotenv playwright
python -m playwright install
```

## הגדרת מפתח OpenAI

בקובץ `.env` צריך להגדיר:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

אם לא תגדירי `OPENAI_MODEL`, ברירת המחדל היא `gpt-4o-mini`.

## איך להריץ

בטרמינל:

```powershell
uv run host.py
```

או אם אין `uv`:

```powershell
.\.venv\Scripts\python.exe host.py
```

## דוגמאות לשאלות שה-Agent יכול לענות

- `what is the weather in Ashdod?`
- `give me the weather forecast for Tel Aviv` 
- `are there any weather alerts in California?`
- `what is the temperature in New York?`
- `what is the weather forecast for Bnei Brak?`

## הערות

- הקובץ `weather_Israel.py` משתמש ב־Playwright כדי לבצע חיפוש עיר באתר ישראלי.
- אם רוצים לבחון רק את USA בלי דפדפן, אפשר לשאול על ערים או מדינות בארצות הברית.
- אם יש בעיה בלקוחות ה־MCP, תבדקו קודם האם `weather_Israel.py` ו־`weather_USA.py` רצים בלי שגיאות.

## מה צריך לבדוק אם משהו לא עובד

1. האם `.env` נטען נכון.
2. האם `OPENAI_API_KEY` תקין.
3. האם Playwright מותקן ויודע להריץ דפדפן.
4. האם `host.py` טוען את שני ה־MCP tools.
